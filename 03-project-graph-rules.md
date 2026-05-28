# Project Graph Rules

The project uses a SQLite-backed project graph for indexing, research, and long-term project understanding.

After completing any small feature, refactor, bugfix, new function, new class, test update, or behavior change, update the project graph.

Do not skip graph updates, even for small changes.

## Files

```text
project_graph.sqlite
scripts/update_project_graph.py
scripts/query_project_graph.py
docs/graph-schema.md
```

## Minimal SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  name TEXT NOT NULL,
  path TEXT,
  summary TEXT,
  updated_at TEXT NOT NULL,
  meta JSON
);

CREATE TABLE IF NOT EXISTS edges (
  src TEXT NOT NULL,
  rel TEXT NOT NULL,
  dst TEXT NOT NULL,
  meta JSON,
  PRIMARY KEY (src, rel, dst)
);

CREATE VIRTUAL TABLE IF NOT EXISTS node_fts
USING fts5(id, name, summary);
```

## Node Types

```text
project
module
file
function
class
feature
bugfix
refactor
test
decision
todo
dependency
```

## Edge Relations

```text
contains
touches
adds
modifies
implements
depends_on
calls
tested_by
fixes
refactors
documents
supersedes
related_to
```

## Graph Update Requirements

For every completed change, record:

- feature/task/bugfix/refactor node
- touched files
- added or modified functions/classes
- important dependencies
- tests or manual verification
- short implementation note
- known limitations, if any

Prefer append/update behavior.

Never rewrite unrelated graph data.

## Graph ID Convention

Use stable readable IDs:

```text
feature:adb_ram_capture
bugfix:ocr_text_position
refactor:image_matcher_pipeline
file:src/capture/adb.py
function:src.capture.adb.capture_screenshot_bytes
class:src.matcher.TemplateMatcher
test:tests/test_adb_capture.py
decision:use_sqlite_project_graph
dependency:opencv
```

## Example

```text
feature:adb_ram_capture
  touches -> file:src/capture/adb.py
  adds -> function:src.capture.adb.capture_screenshot_bytes
  depends_on -> dependency:adb_exec_out
  tested_by -> test:tests/test_adb_capture.py
```

Implementation note example:

```text
Added in-memory ADB screenshot capture using `adb exec-out screencap -p`.
Avoids writing screenshots to disk during repeated capture loops.
```

## Research Usage

Before large changes, query the project graph to understand existing structure.

Use the graph to answer:

- which files belong to a feature
- which functions were added for a task
- why a decision was made
- what tests cover a feature
- what dependencies are involved
- what previous related work exists
