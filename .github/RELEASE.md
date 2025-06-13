# Release Process

This checklist ensures every release is consistent, high quality, and easy to verify.

---

## 1. Pre-release

- [ ] All tests and linters pass (`pytest`, `ruff check .`, `black --check .`)
- [ ] All documentation and changelog entries are up to date
- [ ] Version bumped in `sluggi/__init__.py` and `pyproject.toml`
- [ ] New features, bugfixes, and breaking changes are documented in `CHANGELOG.md`
- [ ] Verify no sensitive data (e.g., `.env`) is tracked or published

## 2. Commit and Tag

- [ ] Commit changes with message: `Release vX.Y.Z`
- [ ] Tag the release:
  ```bash
  git tag vX.Y.Z
  git push --tags
  ```

## 3. GitHub Release

- [ ] Create a new release on GitHub
- [ ] Include highlights/notes from `CHANGELOG.md`
- [ ] Attach any relevant build artifacts if needed

## 4. Publish to PyPI

- [ ] Build and upload:
  ```bash
  python -m build
  twine upload dist/*
  ```
- [ ] Verify the release on PyPI: https://pypi.org/project/sluggi/

## 5. Docs & Announcement

- [ ] Ensure GitHub Pages/docs are published and up to date (if applicable)
- [ ] Announce the release (social, changelog, etc.)
