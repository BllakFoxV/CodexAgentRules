# Project Graph Schema

The project graph is stored in `project_graph.sqlite` and is updated by `scripts/update_project_graph.py` inside a target project.

## Tables

### `nodes`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `TEXT PRIMARY KEY` | Stable readable node id. |
| `type` | `TEXT NOT NULL` | Node type such as `project`, `file`, `class`, `function`, `feature`, `test`. |
| `name` | `TEXT NOT NULL` | Human readable name. |
| `path` | `TEXT` | Relative project path when applicable. |
| `summary` | `TEXT` | Short purpose or implementation note. |
| `updated_at` | `TEXT NOT NULL` | UTC ISO timestamp. |
| `meta` | `JSON` | Additional metadata encoded as JSON text. |

### `edges`

| Column | Type | Notes |
| --- | --- | --- |
| `src` | `TEXT NOT NULL` | Source node id. |
| `rel` | `TEXT NOT NULL` | Relation type. |
| `dst` | `TEXT NOT NULL` | Destination node id. |
| `meta` | `JSON` | Optional JSON metadata. |

Primary key: `(src, rel, dst)`.

### `node_fts`

FTS5 index over `id`, `name`, and `summary`.

## Node Types

`project`, `module`, `file`, `function`, `class`, `feature`, `bugfix`, `refactor`, `test`, `decision`, `todo`, `dependency`.

## Edge Relations

`contains`, `touches`, `adds`, `modifies`, `implements`, `depends_on`, `calls`, `tested_by`, `fixes`, `refactors`, `documents`, `supersedes`, `related_to`.
