# AGENTS.md

Instructions for coding agents and human contributors. Keep this file true:
when a change makes a statement here wrong, fix the statement in the same
pull request.

## Project

`sluggi` turns text into clean, URL-safe slugs: a Python library with a
modular pipeline (Unicode normalisation, HTML entity decoding, optional emoji
names, Greek and Cyrillic transliteration, word extraction, stopwords,
joining), batch and async variants, and a `sluggi` command-line tool. No
runtime dependencies. Published on PyPI as `sluggi`; the current release is
0.1.2.

sluggi is the first box out of [blipbox](https://blipbox.io): AI coding
agents draft the code, tests and docs in pull requests, and Atilla Guzel
reads every change before it merges. The sibling project
[blip-box/confusable](https://github.com/blip-box/confusable) does
look-alike and invisible-character detection; a sluggi option that rejects
confusable input is planned for after confusable's first non-prerelease
release, and nothing in sluggi depends on it yet.

## Layout

| Path | What it is |
|---|---|
| `sluggi/api.py` | The pipeline steps as plain functions, `SlugPipeline`, and the public entry points `slugify`, `batch_slugify`, `async_slugify`, `async_batch_slugify`. |
| `sluggi/cli.py` | The Typer app behind the `sluggi` command: `slug`, `batch`, `bench`, `info`, `version`. Needs the `cli` extra (typer, rich). |
| `sluggi/replacements.py` | `ReplacementRule`, `ReplacementConfig`, `ReplacementEngine`, and `custom_map_to_config` for user mappings. |
| `sluggi/utils.py`, `sluggi/constants.py` | `truncate_slug` and the transliteration tables. |
| `sluggi/__init__.py` | The public API and `__version__`, which must match `pyproject.toml`. |
| `tests/` | 103 tests: unit (`test_api.py`, `test_helpers.py`), async (`test_async_api.py`), CLI through Typer's runner (`test_cli.py`), property-based with Hypothesis (`test_property_based.py`), and `test_release_notes.py` for the release script. |
| `scripts/` | Benchmarks, a profiler, a pipeline debugger and `release_notes.py`; see `scripts/README.md`. Not part of the package. |
| `docs/` | The MkDocs site (`docs/mkdocs.yml`, mkdocs-shadcn theme), deployed to GitHub Pages on every push to `main`. |
| `.github/` | Workflows (`workflows/README.md` lists them), Dependabot, issue templates, contributing, security and release docs. |
| `CHANGELOG.md` | Keep a Changelog format. User-visible changes go under `Unreleased`; each released section ends with the sign-off line that the release notes carry. |

## Commands

```bash
uv sync --all-extras                        # project, CLI and development tools, on the Python in .python-version
uv run pytest                               # the tests (about three seconds)
uv run pre-commit run --all-files           # what the CI lint job runs
uv run pre-commit install                   # hooks on commit, including the commit message check
uv run sluggi slug "Hello, Wörld!"          # the CLI from the checkout
uv run sluggi bench --count 20000 --length 40   # serial and batch timings on this machine
```

The pre-commit hooks are Black, Ruff (`ruff-check`), end-of-file and
trailing-whitespace fixes, `uv lock --check`, zizmor and actionlint on the
workflows, and commitlint on the commit message. CI runs the same hooks once
on Python 3.13, then the tests with coverage on 3.10, 3.11, 3.12 and 3.13.

## Conventions

- **Commits** follow Conventional Commits with a lowercase subject
  (`fix: ...`, `feat: ...`, `build(deps): ...`). commitlint checks locally
  and in CI; the body may have long lines.
- **One pull request per change**, with a body that says what changed and
  why, how it was verified, and what merging risks. The maintainer merges;
  agents never merge, and never write to the branch rules.
- **Formatting is Black's**, not Ruff's: `ruff format` disagrees with Black
  on a few files, so do not run it. Ruff lints with `E, F, W, D, I, UP, N`
  (see `pyproject.toml` for the ignores and why).
- **Public functions and classes have type hints and a docstring.** Use
  `X | None`, not `Optional[X]`; the floor is 3.10.
- **Tests come with the change**, and a `CHANGELOG.md` entry when users will
  notice.
- **Untrusted text never reaches a workflow `run:` line.** Issue bodies, pull
  request titles and model output go through `env:` and files; see
  `.github/workflows/summary.yml`.

## Decisions

| Topic | Decision |
|---|---|
| Python | `>=3.10`, since November 2026 (3.9 reached end of life in October 2025). Development and the CI lint job run on 3.13, because zizmor's package needs 3.11 or newer; the matrix tests the floor. |
| Dependencies | None at runtime, and keep it that way. Extras: `cli` (typer, rich), `emoji`, `test`, `dev`. The `>=` floors in `pyproject.toml` are published metadata: raise them deliberately, not because a lock update happened. |
| Lock and Dependabot | `uv.lock` is committed. Dependabot (`uv`, `github-actions` and `pre-commit` ecosystems) updates it weekly, grouped, after a seven-day cooldown, leaving floors alone (`increase-if-necessary`). No `commit-message.prefix` is set on purpose: with one, Dependabot capitalises "Bump" and commitlint rejects it. |
| Auto-merge | Every Dependabot pull request gets squash auto-merge and lands once the required checks pass. The maintainer closes the ones that break (a major Black release that reformats the tests, say) or fixes the code first. |
| certifi | A lock-only floor (`[tool.uv] constraint-dependencies`) from the October 2026 eMudhra/emSign CA compromise. Nothing pulls certifi in today; the floor stays so a future dependency cannot resolve to an old bundle. |
| Workflows | Every action is pinned to a commit hash with the version in a comment; every workflow starts from `permissions: {}`; checkouts keep no credentials. zizmor and actionlint enforce this. The four `continuous-integration (3.x)` job names are the required checks in the `Protect main` ruleset, so renaming them means editing the ruleset. |
| Scheduled workflows | None. A benchmark and a mutation-testing workflow ran every Sunday for months without a single success and nobody noticed. Add a scheduled workflow only with something that fails loudly when it stops (`.github/workflows/README.md`). |
| Mutation testing | Not run. mutmut 3 does not get past generating mutants on this code base; it was removed in November 2026 rather than left failing. |
| Docs build | Its dependencies (mkdocs-shadcn and friends) are pinned in `deploy-docs.yml`, not in `uv.lock`, and Dependabot does not see them. |
| commitlint hook | `language_version` is pinned to a Node release by hand, because nodeenv cannot parse the pre-release that heads nodejs.org's index. Dependabot does not bump it. |
| Benchmarks | The README table was measured in June 2025 on one laptop with a script that no longer exists. `sluggi bench` gives serial and batch timings; `scripts/run_benchmarks.py` compares with python-slugify. Measure before quoting numbers. |

## Releasing

A maintainer does it; see `.github/RELEASE.md`. In short: a `CHANGELOG.md`
section with the sign-off line, the version bumped in `pyproject.toml` and
`sluggi/__init__.py`, a `vX.Y.Z` tag. `release.yml` builds, publishes to PyPI
through trusted publishing, signs with Sigstore, and drafts the GitHub release
from the changelog section; the maintainer reads the draft and publishes it.

## Security

Report vulnerabilities through GitHub Security Advisories, never a public
issue (`.github/SECURITY.md`).
