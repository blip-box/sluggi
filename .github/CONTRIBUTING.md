# Contributing to sluggi

Thank you for helping make sluggi better! We welcome all contributions—code, docs, tests, and ideas.

---

## Getting Started

- **Fork and clone** the repo from [blip-box/sluggi](https://github.com/blip-box/sluggi).
- **Install dev dependencies:**
  ```bash
  pip install .[dev,cli]
  ```
- **Code style:**
  - Format code with [Black](https://black.readthedocs.io/)
  - Lint with [Ruff](https://docs.astral.sh/ruff/)
  - Type annotations for all public APIs
- **Testing:**
  - Run tests with `pytest`
- **Open issues/PRs** for bugs, features, or improvements.
- See our [Code of Conduct](https://github.com/blip-box/sluggi/blob/main/CODE_OF_CONDUCT.md) and [Security Policy](https://github.com/blip-box/sluggi/blob/main/SECURITY.md) for community and reporting guidelines.

---

## Pull Request Checklist

- Branch from `main` and keep your branch up to date.
- Run all tests and linters before submitting.
- Use clear, descriptive commit messages.
- Reference related issues in your PR description.
- At least one maintainer review is required.
- Follow our [Release Process](https://github.com/blip-box/sluggi/blob/main/RELEASE.md) for version bumps and publishing.

---

## Code Style Guide

- **Formatting:** [Black](https://black.readthedocs.io/)
- **Linting:** [Ruff](https://docs.astral.sh/ruff/)
- **Type Hints:** Required for all public APIs.
- **Imports:** Standard, third-party, then local.
- **Docstrings:** Concise and clear for all public functions/classes.

---

## Pre-commit Hooks

Set up pre-commit hooks to enforce style and quality:

| Hook                  | Purpose                |
|-----------------------|------------------------|
| black                 | Code formatting        |
| ruff                  | Linting                |
| isort                 | Import sorting         |
| trailing-whitespace   | Remove whitespace      |
| end-of-file-fixer     | Ensure newline         |

Install and run hooks:

```bash
pre-commit install
pre-commit run --all-files
```

---

## Release Checklist

- [ ] All tests and linters pass
- [ ] Docs and [Changelog](https://github.com/blip-box/sluggi/blob/main/CHANGELOG.md) updated
- [ ] Version bumped in `__init__.py` and `pyproject.toml`
- [ ] Commit with message: `Release vX.Y.Z`
- [ ] Push to `main` and create a GitHub release
- [ ] Publish to PyPI:
  ```bash
  python -m build
  twine upload dist/*
  ```
- [ ] Verify GitHub Pages documentation is up to date

---

!!! warning "Security and Conduct"
    - Report vulnerabilities or conduct issues via [GitHub Security Advisories](https://github.com/blip-box/sluggi/security/advisories) for privacy.
    - Never include sensitive info in public issues or PRs.

---

Thank you for contributing!
— The blipbox/sluggi team
