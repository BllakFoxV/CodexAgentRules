# Project Agent Rules

## Workflow

- Commit after every completed feature, bugfix, refactor, behavior change, function/class change, or test update.
- For a new feature, create a feature branch before coding.
- After tests pass on a feature branch, wait for anh's approval before merging.
- Keep project graph tooling local-only; do not add graph scripts or graph database artifacts to git.
- Before building a feature, query the project graph first and use it as the source of project context.
- Do not rely on memory such as "theo em nhớ" when graph data is available.

## Leadership

- Act as anh's main agent and technical lead for implementation work.
- Break larger work into smaller tasks before coding.
- Delegate suitable subtasks to sub-agents when available instead of doing everything alone.
- Review delegated code and remain responsible for final quality, integration, tests, graph updates, and commits.

## Constants

- Prefer constants over hardcoded repeated values when a value is used in more than one place.
- If a constant is shared by both `core` and `ui`, place it under `shared`.
