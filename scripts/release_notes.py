#!/usr/bin/env python3
"""Print the CHANGELOG.md section for one version, for use as release notes.

Usage: python scripts/release_notes.py v0.1.2 [CHANGELOG.md]
The tag may carry a leading "v". Exits with status 1 when the section is
missing, so a release without a changelog entry fails loudly.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def extract(changelog: str, version: str) -> str:
    """Return the body of the ``## [version]`` section, without its heading."""
    version = version.lstrip("v")
    pattern = re.compile(
        r"^## \[" + re.escape(version) + r"\][^\n]*\n(.*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(changelog)
    if not match:
        raise KeyError(f"no changelog section for version {version}")
    return match.group(1).strip() + "\n"


def main(argv: list[str]) -> int:
    """Print the section for ``argv[1]`` from ``argv[2]`` or ``CHANGELOG.md``."""
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[2]) if len(argv) > 2 else Path("CHANGELOG.md")
    try:
        sys.stdout.write(extract(path.read_text(encoding="utf-8"), argv[1]))
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
