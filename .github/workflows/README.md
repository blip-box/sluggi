# GitHub Workflows for Sluggi

This folder contains all GitHub Actions workflows that automate, safeguard, and accelerate the development of the Sluggi project. These workflows are designed to be:

- **Best-in-class:** Modern, modular, and easy to maintain.
- **Agent/Human Friendly:** Seamlessly usable by both human contributors and autonomous agents/bots.
- **Future-proof:** Ready for new automation paradigms and open experimentation.

---

## Workflow Overview

| Workflow         | Purpose                                                                                 | Human/Agent Friendly |
|------------------|----------------------------------------------------------------------------------------|:--------------------:|
| `ci.yml`         | Lint, format, test, and upload coverage on push/PR. Maintains code quality.             | ✅                   |
| `benchmark.yml`  | Runs performance benchmarks and updates badge.                                          | ✅                   |
| `changelog.yml`  | Auto-generates changelog on PR merge to main.                                          | ✅                   |
| `docs.yml`       | Deploys MkDocs docs to GitHub Pages on main.                                           | ✅                   |
| `auto-merge.yml` | Enables auto-merge for Dependabot PRs.                                                 | ✅                   |
| `issue-triage.yml` | Adaptive triage for issues and PRs—labels and parses agent/human reports, auto-closes incomplete PRs, and triggers agent workflows. | ✅                   |
| `playground.yml` | Safe, isolated workflow for agents/humans to experiment, test, or self-heal.           | ✅                   |

---

## Advanced Triage Automation (Agent & Human)

### Adaptive Issue & PR Triage (`issue-triage.yml`)
- **Auto-labels** all issues and PRs based on agent/human identification and type checkboxes in templates.
- **Parses JSON metadata** from issue/PR bodies and summarizes it in a comment for maintainers and agents.
- **Auto-closes incomplete PRs**: If a PR is missing agent/human identification or a summary, it is automatically closed with a clear comment, ensuring only well-formed PRs remain open.
- **Triggers additional workflows for agent changes**: If a PR is labeled as an `Agent/automation change`, a custom event (`agent-change-pr`) is dispatched, enabling downstream automation (e.g., special audits, analytics, or further agent review).
- **Welcoming, actionable feedback** is posted for both humans and agents.

### Playground Workflow (`playground.yml`)
- Provides a safe, isolated environment for agents and humans to experiment, test, or self-heal code.
- Triggered by labeling an issue/PR with `playground` or via manual dispatch.
- All artifacts and experiments are automatically cleaned up.

---

## How to Use

- **For Humans:**
  - Just push code, open PRs, or label issues as usual. Most automation is zero-config and will guide you if needed.
  - Use the `playground` label if you want to safely experiment or test automation.
- **For Agents/Bots:**
  - All workflows are designed to be triggered by agents as well as humans.
  - Use the `playground` workflow for safe experimentation or self-healing tasks.
  - Issue templates and triage workflows are structured for easy parsing and auto-labeling.

---

## Contributing or Extending

- Add new workflows for new automation needs—be creative!
- Document your workflow’s intent with a top-level comment.
- Keep workflows modular and agent/human friendly.
- If you have ideas for new agent-driven or AI-powered workflows, open a PR or issue.

---

## Why This Matters

This workflows folder is more than just CI—it's an automation platform for the next generation of open source, where humans and agents collaborate, experiment, and improve together.

---

For more details, see individual workflow files or open an issue/question with the `quick-issue` template.
