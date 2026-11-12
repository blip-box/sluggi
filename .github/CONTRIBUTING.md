# Contributing to sluggi

Thank you for helping make sluggi better. Code, docs, tests and ideas are all
welcome. [AGENTS.md](../AGENTS.md) describes how the repository works in
detail; this page is the short version.

## Getting started

```bash
git clone https://github.com/blip-box/sluggi.git
cd sluggi
uv sync --all-extras        # the project, the CLI and every development tool
uv run pre-commit install   # formatting, linting and the commit message check
uv run pytest               # the test suite
uv run sluggi --help        # the CLI from the checkout
```

`uv sync` picks the interpreter in `.python-version`. The package itself
supports Python 3.10 and newer, which CI tests.

## Code style

- [Black](https://black.readthedocs.io/) formats, [Ruff](https://docs.astral.sh/ruff/)
  lints. Both run as pre-commit hooks and in CI.
- Type hints and a docstring on every public function and class.
- Imports: standard library, third party, then local; Ruff sorts them.

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

## Pull requests

- Branch from `main`. One pull request per change.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`fix: ...`, `feat: ...`, `docs: ...`); the commit-msg hook and CI both check.
- Add tests for behaviour that changes, and an entry under `Unreleased` in
  `CHANGELOG.md` when users will notice the change.
- CI must pass. A maintainer reads every pull request before merging it; the
  branch rules are public.

## Pre-commit hooks

`uv run pre-commit run --all-files` runs what CI runs:

| Hook | Purpose |
|---|---|
| black | formatting |
| ruff-check | linting |
| end-of-file-fixer, trailing-whitespace | file hygiene |
| uv-lock | `uv.lock` matches `pyproject.toml` |
| zizmor, actionlint | security and correctness of the GitHub workflows |
| commitlint (commit-msg) | Conventional Commits |

## Releases

See [RELEASE.md](RELEASE.md). A release is tagged by a maintainer; the
workflow builds, publishes and signs it.

## Security and conduct

- Report vulnerabilities through
  [GitHub Security Advisories](https://github.com/blip-box/sluggi/security/advisories/new),
  never in a public issue. See [SECURITY.md](SECURITY.md).
- The [Code of Conduct](CODE_OF_CONDUCT.md) applies everywhere in the project.
