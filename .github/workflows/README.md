# Workflows

What runs on this repository, and when. Keep this file true: a change to a
workflow that makes a row here wrong fixes the row in the same pull request.

Every workflow runs with the repository's default token, which is read-only.
A job that needs to write asks for exactly that scope in its own
`permissions` block.

| Workflow | Runs on | What it does |
|---|---|---|
| `ci.yml` | pushes to `main`, pull requests | Installs the project with uv on Python 3.10 to 3.13, runs the pre-commit hooks, Ruff and Black, then the tests with coverage, and uploads the coverage report to Codecov. The four `continuous-integration (3.x)` jobs are the required checks on `main`. |
| `commit-lint.yml` | pull requests, pushes to `main` | Checks commit messages against `.commitlintrc.yml` (Conventional Commits). The same check runs locally as a commit-msg hook. |
| `auto-merge.yml` | pull requests opened by Dependabot | Enables squash auto-merge, so the update lands on its own once the required checks pass. |
| `label.yml` | pull requests | Applies the labels in `.github/labeler.yml`, by changed paths and branch prefix. |
| `greetings.yml` | a contributor's first issue or pull request | Posts a welcome comment. |
| `summary.yml` | new issues | Asks GitHub Models for a one-paragraph summary and posts it as a comment. The issue text reaches the model through a file, never a shell line. GitHub Models may be unavailable to the repository, so the step is allowed to fail. |
| `deploy-docs.yml` | pushes to `main`, manual | Builds the MkDocs site in `docs/` and deploys it to GitHub Pages at https://blip-box.github.io/sluggi/. |
| `release.yml` | tags `v*.*.*` | Builds the sdist and wheel, publishes them to PyPI through trusted publishing, signs them with Sigstore and drafts the GitHub release with the notes from `CHANGELOG.md`. The steps around it are in [RELEASE.md](../RELEASE.md). |

Dependabot is configured in `../dependabot.yml`, not in a workflow: weekly,
grouped, with a seven-day cooldown, updating `uv.lock` rather than the
version floors in `pyproject.toml`.

## Rules

- **No scheduled workflow without a watcher.** A benchmark workflow and a
  mutation-testing workflow ran every Sunday for months and never once
  succeeded: the first pushed a badge that the branch rules reject and that
  nothing displayed, the second never finished inside GitHub's six-hour job
  limit. Nobody noticed, because nothing was watching. Both were removed in
  November 2026, with a playground workflow whose every step was an `echo`.
  Add a scheduled workflow only together with something that fails loudly
  when it stops working, such as a CI job that checks the workflow is still
  enabled and its last run passed.
- **Untrusted text never reaches a `run:` line.** Issue bodies, pull request
  titles and model output go through `env:` and files, as `summary.yml`
  shows. The GitHub Actions template engine expands `${{ }}` before the
  shell sees the script.
- **Workflows that must write ask for the scope they need** in the job's
  `permissions` block, and nothing more.
