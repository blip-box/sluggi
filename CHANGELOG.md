# Changelog

All notable changes to sluggi are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

Every entry names the engineer who read the changes and signed the release.
The GitHub release notes for a tag are generated from that tag's section by
`scripts/release_notes.py`.

## [Unreleased]

### Changed
- README, docs, and package description state measured facts instead of
  adjectives: the benchmark figures replace "blazing-fast", and the Unicode
  support is described as what it is (NFKD normalization, Greek and Cyrillic
  transliteration, optional emoji).
- Release notes are generated from this changelog, so every release carries
  its sign-off line.
- The contributing guide and release process describe how the repository
  actually works, including how agent-drafted changes are handled.

### Fixed
- `LICENSE` now contains only the MIT license. It previously also carried
  most of the Apache 2.0 text by mistake, which stopped GitHub from
  identifying the license.

## [0.1.2] - 2025-10-13

### Fixed
- Removed a debug print from the `batch` CLI command (#47).

### Changed
- GitHub Actions dependencies updated.

Drafted with AI coding agents. Reviewed and signed off by Atilla Guzel.

## [0.1.1] - 2025-06-13

### Changed
- Documentation links corrected and the docs aligned with the `slug` command.
- Repository housekeeping: community files moved to `.github`, labeler,
  commitlint, and pre-commit configuration added.

Drafted with AI coding agents. Reviewed and signed off by Atilla Guzel.

## [0.1.0] - 2025-06-08

### Added
- First release. `slugify` and `batch_slugify` with serial, thread, and
  process modes, an asyncio API, custom character mappings, stopword
  filtering, Greek and Cyrillic transliteration, optional emoji conversion,
  and a CLI with shell completion.

Drafted with AI coding agents. Reviewed and signed off by Atilla Guzel.

[Unreleased]: https://github.com/blip-box/sluggi/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/blip-box/sluggi/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/blip-box/sluggi/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/blip-box/sluggi/releases/tag/v0.1.0
