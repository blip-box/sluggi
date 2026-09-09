"""Tests for scripts/release_notes.py."""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "release_notes",
    Path(__file__).resolve().parents[1] / "scripts" / "release_notes.py",
)
release_notes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_notes)

SAMPLE = """# Changelog

## [Unreleased]

### Changed
- Something pending.

## [0.2.0] - 2026-01-01

### Added
- A feature.

Signed off by Someone.

## [0.1.0] - 2025-06-08

### Added
- First release.
"""


def test_extracts_section_body_for_tag_with_v_prefix():
    """A tag with a leading v maps to its changelog section body."""
    body = release_notes.extract(SAMPLE, "v0.2.0")
    assert body == "### Added\n- A feature.\n\nSigned off by Someone.\n"


def test_extracts_last_section():
    """The final section is extracted without a trailing heading."""
    assert release_notes.extract(SAMPLE, "0.1.0") == "### Added\n- First release.\n"


def test_missing_version_raises():
    """A version with no section raises KeyError so releases fail loudly."""
    with pytest.raises(KeyError):
        release_notes.extract(SAMPLE, "9.9.9")


def test_real_changelog_has_every_released_version():
    """Every published version has a section that names who signed it off."""
    changelog = (Path(__file__).resolve().parents[1] / "CHANGELOG.md").read_text()
    for version in ("0.1.0", "0.1.1", "0.1.2"):
        assert "signed off by" in release_notes.extract(changelog, version).lower()
