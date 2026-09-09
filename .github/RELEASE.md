# Release Process

A release is a blip: small, tested, and signed off by a person. The workflow
does the mechanical work; the engineer does the reading and the publishing.

## 1. Before tagging

- [ ] Tests and linters pass on `main` (`pytest`, `ruff check .`, `black --check .`)
- [ ] `CHANGELOG.md` has a `## [X.Y.Z] - YYYY-MM-DD` section for this release,
      ending with the line `Drafted with AI coding agents. Reviewed and signed off by <name>.`
- [ ] Version bumped in `pyproject.toml` and `sluggi/__init__.py`
- [ ] Docs updated where behaviour changed

## 2. Tag

Merge the release pull request, then:

```bash
git checkout main && git pull
git tag vX.Y.Z
git push origin vX.Y.Z
```

## 3. The workflow (`.github/workflows/release.yml`)

On the tag push it builds the wheel and sdist, publishes them to PyPI through
trusted publishing, signs them with Sigstore, and creates a **draft** GitHub
release whose notes are the changelog section for that tag
(`scripts/release_notes.py`). A tag without a changelog section fails the
workflow on purpose.

## 4. Publish

- [ ] Open the draft release, read the notes and the attached artifacts
- [ ] Check the version on PyPI: https://pypi.org/project/sluggi/
- [ ] Publish the release. Publishing is the sign-off.

## 5. Afterwards

- [ ] Confirm the docs site deployed
- [ ] Announce it if there is something worth announcing
