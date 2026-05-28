# CodexAgentRules - Linux Edition

Rule framework and local project-graph tooling for Codex agents on Linux. This repo captures the workflow anh designed: concise Vietnamese collaboration, graph-first project understanding, disciplined branching/commits, and senior-agent delegation/review.

## Project Contents

### `rules/` - Agent Guidelines

- **[01-core-agent-rules.md](rules/01-core-agent-rules.md)** - Identity, communication, workflow, final response format.
- **[02-coding-rules.md](rules/02-coding-rules.md)** - Code style, Python conventions, performance and IO rules.
- **[03-project-graph-rules.md](rules/03-project-graph-rules.md)** - SQLite graph schema, node/edge types, update requirements.
- **[INDEX.md](rules/INDEX.md)** - Quick reference for which rule file to read.

### `example_project_rule/`

- **[AGENTS.md](example_project_rule/AGENTS.md)** - Project-level rules to copy into app repos.

### `scripts/`

- **setup_project_rules.py** - Install `AGENTS.md`, graph scripts, graph schema, and `.gitignore` entries into a target project.
- **update_project_graph.py** - Scan a target project and generate/update `project_graph.sqlite`.
- **query_project_graph.py** - Search graph nodes and inspect edges.

### `docs/`

- **graph-schema.md** - Human-readable graph schema reference copied into projects as local agent documentation.

## Core Workflow Rules

Use these rules in every target project after setup:

- Read the relevant rules before coding.
- Make a short plan before code/file changes.
- Query the project graph before building a feature; do not rely on memory when graph data exists.
- Create a feature branch before feature work.
- Commit after every completed feature, bugfix, refactor, behavior change, function/class change, or test update.
- Run relevant tests/checks before reporting completion.
- Update the project graph after every completed code/test/behavior change.
- After tests pass on a feature branch, wait for anh's approval before merging.
- Keep graph tooling local-only in target projects; do not add graph scripts or graph database artifacts to app repos unless anh explicitly wants that.

## Main Agent / Delegation Model

The main agent acts like anh's senior technical lead:

- Break larger work into smaller tasks.
- Use the graph as project context before assigning or coding work.
- Delegate suitable side tasks to sub-agents when available.
- Keep ownership of final quality: review delegated work, integrate changes, run tests, update graph, and commit.
- Do not use sub-agents as a substitute for review. The main agent remains responsible.

## Constants Rule

- Prefer constants over repeated hardcoded values when a value is used in more than one place.
- If a constant is shared by both `core` and `ui`, place it under `shared`.

## Setup Into A Project

From this repo:

```bash
python3 scripts/setup_project_rules.py /path/to/project \
  --project-id project:your_project \
  --local-roots core,ui,shared,models,tests,main
```

For WaydroidMgr-style projects:

```bash
python3 scripts/setup_project_rules.py /home/foxnq/Projects/WaydroidMgr \
  --project-id project:waydroidmgr \
  --local-roots core,models,shared,ui,tests,main
```

The setup script installs or updates:

- `AGENTS.md`
- `docs/graph-schema.md`
- `scripts/update_project_graph.py`
- `scripts/query_project_graph.py`
- `.gitignore` entries for local graph artifacts

By default, existing files are preserved. Use `--force` to overwrite existing agent/graph files:

```bash
python3 scripts/setup_project_rules.py /path/to/project --force
```

## Generated Files In Target Projects

Target projects should normally ignore these local agent artifacts:

```text
project_graph.sqlite
project_graph.sqlite-*
docs/graph-schema.md
scripts/update_project_graph.py
scripts/query_project_graph.py
```

`AGENTS.md` should usually be committed because it documents the project workflow for future agent sessions.

## Generate And Query Project Graph

Inside a target project after setup:

```bash
python3 scripts/update_project_graph.py
python3 scripts/query_project_graph.py "feature OR MainWindow" --limit 20
python3 scripts/query_project_graph.py "feature:event_bus" --edges
```

Use graph queries before feature work to understand existing files, functions, tests, dependencies, and previous decisions. Use graph updates after changes to keep that memory current.

## Graph Database Schema

### Nodes Table

| Column | Type | Purpose |
| --- | --- | --- |
| `id` | TEXT (PK) | Stable id: `file:path`, `class:module.Name`, `function:module.name`. |
| `type` | TEXT | Entity type: `project`, `module`, `file`, `class`, `function`, `feature`, `test`, etc. |
| `name` | TEXT | Human-readable name. |
| `path` | TEXT | File path relative to project root. |
| `summary` | TEXT | Docstring or short description. |
| `updated_at` | TEXT | UTC update timestamp. |
| `meta` | JSON | Extra metadata such as module, line number, async flag, syntax error info. |

### Edges Table

| Column | Type | Purpose |
| --- | --- | --- |
| `src` | TEXT | Source node id. |
| `rel` | TEXT | Relationship type. |
| `dst` | TEXT | Destination node id. |
| `meta` | JSON | Optional relationship metadata. |

### Node Types

```text
project module file function class feature bugfix refactor test decision todo dependency
```

### Relationship Types

```text
contains touches adds modifies implements depends_on calls tested_by fixes refactors documents supersedes related_to
```

## File Structure

```text
CodexAgentRules/
├── docs/
│   └── graph-schema.md
├── example_project_rule/
│   └── AGENTS.md
├── rules/
│   ├── 01-core-agent-rules.md
│   ├── 02-coding-rules.md
│   ├── 03-project-graph-rules.md
│   └── INDEX.md
├── scripts/
│   ├── query_project_graph.py
│   ├── setup_project_rules.py
│   └── update_project_graph.py
├── requirements.txt
└── README.md
```

## Development

- Update rules in `rules/`.
- Update project-level defaults in `example_project_rule/AGENTS.md`.
- Update installer behavior in `scripts/setup_project_rules.py`.
- Regenerate a target project's graph with `python3 scripts/update_project_graph.py` inside that target project.

## License

Same as Codex Linux project.
