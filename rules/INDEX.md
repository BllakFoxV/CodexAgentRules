# Codex Rule Index

Use this file to find the smallest rule file or section needed for the current task. Prefer targeted reads with `sed` or search instead of reading every rule file.

## R01 - Core Agent Rules

File: `/home/foxnq/.codex/rules/01-core-agent-rules.md`

Sections:

- `R01.1` Identity & Communication
- `R01.2` Workflow
- `R01.3` Final Response Format

Read when:

- Starting work that may involve code or file changes.
- Preparing the final response after code changes.
- Unsure about communication style or workflow expectations.

## R02 - Coding Rules

File: `/home/foxnq/.codex/rules/02-coding-rules.md`

Sections:

- `R02.1` General Style
- `R02.2` Python Rules
- `R02.3` Performance & IO

Read when:

- Editing code.
- Creating scripts or CLIs.
- Working with Python.
- Handling repeated IO, screenshots, logs, ADB capture, or temporary files.

## R03 - Project Graph Rules

File: `/home/foxnq/.codex/rules/03-project-graph-rules.md`

Sections:

- `R03.1` Purpose and trigger
- `R03.2` Project graph files
- `R03.3` Minimal SQLite schema
- `R03.4` Node types
- `R03.5` Edge relations
- `R03.6` Graph update requirements
- `R03.7` Graph ID convention
- `R03.8` Example update
- `R03.9` Research usage

Read when:

- Before large changes, to query graph usage expectations.
- After any completed feature, refactor, bugfix, function/class change, behavior change, or test update.
- When reporting whether graph update succeeded or failed.

## Quick Triggers

- `coding`: read `R01`, `R02`.
- `python`: read `R02.2`.
- `adb` or repeated capture/log loops: read `R02.3`.
- `project graph`, `graph update`, completed code change: read `R03`.
- `final response after code changes`: read `R01.3` and `R03.6`.
