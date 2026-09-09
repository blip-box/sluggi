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

## Agent-drafted changes

Most of sluggi is drafted by AI coding agents and reviewed by a person. Changes
drafted with an agent are welcome under the same rules as any other change:

- Say so in the pull request description.
- Include tests. A draft earns its merge with tests, and the tests are read as
  carefully as the code.
- Be able to explain every line. If a reviewer asks why, "the agent wrote it"
  is not an answer.
- Pull requests generated and submitted without a person reading them are
  closed without review.

Every change arrives as a pull request with CI passing and is read by a
maintainer before it merges. The branch rules are public.

---

## Pull Request Checklist

- Branch from `main` and keep your branch up to date.
- Run all tests and linters before submitting.
- Use clear, descriptive commit messages.
- Reference related issues in your PR description.
- At least one maintainer review is required.
- Follow our [Release Process](https://github.com/blip-box/sluggi/blob/main/.github/RELEASE.md) for version bumps and publishing.

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
- [ ] Add the changelog section with its sign-off line
- [ ] Tag `vX.Y.Z` and push the tag; the release workflow builds, publishes to
      PyPI, signs, and drafts the GitHub release with notes from the changelog
- [ ] Read the draft release and publish it
- [ ] Verify GitHub Pages documentation is up to date

---

!!! warning "Security and Conduct"
    - Report vulnerabilities or conduct issues via [GitHub Security Advisories](https://github.com/blip-box/sluggi/security/advisories) for privacy.
    - Never include sensitive info in public issues or PRs.

---

Thank you for contributing!
— The blipbox/sluggi team
