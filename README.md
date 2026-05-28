# CodexAgentRules - Linux Edition

Complete rule framework and tooling for Codex AI agents on Linux. Includes behavioral guidelines, coding standards, and automated project understanding.

## Project Contents

### `rules/` — Agent Guidelines
Rules for how Codex agents should work, communicate, and maintain code quality.

- **[01-core-agent-rules.md](rules/01-core-agent-rules.md)** — Identity, communication style, workflow (read before starting work)
- **[02-coding-rules.md](rules/02-coding-rules.md)** — Code style, Python conventions, performance guidelines (read when editing)
- **[03-project-graph-rules.md](rules/03-project-graph-rules.md)** — SQLite schema, node/edge types, graph update triggers (read after code changes)
- **[INDEX.md](rules/INDEX.md)** — Quick reference to find the right rule

### `scripts/` — Project Graph Tools
Python tools for generating and querying a searchable project understanding database.

- **update_project_graph.py** — Scan codebase and generate SQLite graph
  - Extracts files, classes, functions, imports
  - Detects test coverage relationships
  - Handles Python syntax errors gracefully
  
- **query_project_graph.py** — Full-text search and relationship queries
  - Search by name or content (FTS5)
  - Show edges for any node
  - Configurable result limit

## Quick Start

### Prerequisites
- Python 3.10+
- Linux (Ubuntu 20.04+, Fedora 33+, Debian 11+, or similar)
- No external package dependencies

### Generate Project Graph

```bash
# Generate SQLite graph for current project
python scripts/update_project_graph.py

# Specify custom graph location
python scripts/update_project_graph.py --graph /path/to/project_graph.sqlite
```

### Query Project Graph

```bash
# Search nodes by name
python scripts/query_project_graph.py "module:ui"

# Show all edges for a node
python scripts/query_project_graph.py "file:core/services/base.py" --edges

# Limit results
python scripts/query_project_graph.py "function:*service*" --limit 50
```

## Integration with Codex Linux

### Installation

1. **Clone into Codex workspace**
   ```bash
   git clone https://github.com/yourusername/CodexAgentRules.git \
     /opt/codex/data/project-analysis
   ```

2. **Reference in agent initialization**
   ```python
   # In Codex startup
   load_rules_from("/opt/codex/data/project-analysis/rules")
   load_project_graph("/opt/codex/data/project-analysis/project_graph.sqlite")
   ```

3. **Configure for your projects**
   - Update `PROJECT_ID` in `update_project_graph.py` for each codebase
   - Adjust `LOCAL_ROOTS` to match your module structure
   - Set `PROJECT_ROOT` relative to your workspace

4. **Auto-update in CI/CD**
   ```bash
   # Add to build pipeline
   python /opt/codex/data/project-analysis/scripts/update_project_graph.py
   ```

## Graph Database Schema

### Nodes Table
| Column | Type | Purpose |
|--------|------|---------|
| `id` | TEXT (PK) | Unique identifier: `file:path`, `class:module.Name`, `function:module.name` |
| `type` | TEXT | Entity type: file, class, function, module, dependency, feature, decision, todo |
| `name` | TEXT | Human-readable name |
| `path` | TEXT | File path relative to project root |
| `summary` | TEXT | Docstring or description |
| `updated_at` | TEXT | UTC timestamp of last update |
| `meta` | JSON | Additional metadata: module name, line number, async flag, error info |

### Edges Table
| Column | Type | Purpose |
|--------|------|---------|
| `src` | TEXT | Source node ID |
| `rel` | TEXT | Relationship type |
| `dst` | TEXT | Destination node ID |
| `meta` | JSON | Relationship metadata |

### Relationship Types
- `contains` — Parent contains child (project→module, file→class, class→method)
- `depends_on` — Dependency (file→external package)
- `tested_by` — Test coverage (function→test file)
- `touches` — Feature affects file
- `related_to` — Semantic link (decision→feature)

### Node Types
```
project     — Root project node
module      — Package or module
file        — Source or config file
class       — Python class definition
function    — Python function or method
dependency  — External package
feature     — High-level capability
decision    — Architectural choice
todo        — Outstanding task or issue
test        — Test file or case
```

## File Structure

```
CodexAgentRules/
├── rules/
│   ├── 01-core-agent-rules.md       Agent behavior & communication
│   ├── 02-coding-rules.md           Code style & conventions
│   ├── 03-project-graph-rules.md    Graph schema & requirements
│   └── INDEX.md                     Rule quick reference
│
├── scripts/
│   ├── update_project_graph.py      Generate/update SQLite graph
│   └── query_project_graph.py       Search and query graph
│
├── project_graph.sqlite             Generated database (git-ignored)
├── requirements.txt                 Python dependencies (none)
└── README.md                        This file
```

## Linux-Specific Features

- ✅ **POSIX paths** — All paths use `/` separators
- ✅ **Systemd integration** — Use systemd timers for periodic updates
- ✅ **Container-ready** — Works in Docker, Podman, Kubernetes
- ✅ **Standard tooling** — Compatible with vim, emacs, VS Code, git
- ✅ **Tested environments** — Ubuntu 20.04+, Fedora 33+, Debian 11+, AlmaLinux 8+

## Usage Patterns

### For Agent Initialization
1. Load rules: `load_rules_from("rules/")`
2. Query graph: `search_nodes("function:*handler*", limit=10)`
3. Gather context: `related_edges("file:core/main.py")`

### For Code Changes
1. Edit code
2. Run `update_project_graph.py` to sync database
3. Query graph to verify relationships

### For Architecture Review
- Query by feature: `related_edges("feature:event_bus")`
- Find dependencies: `search_nodes("depends_on:*async*")`
- Check test coverage: `related_edges("function:module.MyClass.method", "--edges")`

## Development

**Update rules** → Edit markdown files in `rules/`

**Update tools** → Edit Python scripts in `scripts/` (Python 3.10+, no external deps)

**Regenerate graph** → Run `python scripts/update_project_graph.py`

## License

Same as Codex Linux project.
