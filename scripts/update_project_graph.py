#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = PROJECT_ROOT / "project_graph.sqlite"
PROJECT_ID = "project:codex_agent_rules"
LOCAL_ROOTS = {"scripts"}
SKIP_DIRS = {".git", ".venv", "__pycache__"}


@dataclass(frozen=True)
class Node:
    id: str
    type: str
    name: str
    path: str | None = None
    summary: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    src: str
    rel: str
    dst: str
    meta: dict[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def normalize_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def module_name_for(path: Path) -> str:
    rel = path.relative_to(PROJECT_ROOT).with_suffix("")
    if rel.name == "__init__":
        rel = rel.parent
    return ".".join(rel.parts)


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
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
        """
    )


def upsert_nodes(connection: sqlite3.Connection, nodes: Iterable[Node]) -> None:
    timestamp = utc_now()
    rows = [
        (
            node.id,
            node.type,
            node.name,
            node.path,
            node.summary,
            timestamp,
            json.dumps(node.meta, sort_keys=True),
        )
        for node in nodes
    ]
    connection.executemany(
        """
        INSERT INTO nodes (id, type, name, path, summary, updated_at, meta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          type = excluded.type,
          name = excluded.name,
          path = excluded.path,
          summary = excluded.summary,
          updated_at = excluded.updated_at,
          meta = excluded.meta
        """,
        rows,
    )


def upsert_edges(connection: sqlite3.Connection, edges: Iterable[Edge]) -> None:
    rows = [
        (edge.src, edge.rel, edge.dst, json.dumps(edge.meta, sort_keys=True))
        for edge in edges
    ]
    connection.executemany(
        """
        INSERT INTO edges (src, rel, dst, meta)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(src, rel, dst) DO UPDATE SET meta = excluded.meta
        """,
        rows,
    )


def prune_stale_paths(connection: sqlite3.Connection, nodes: Iterable[Node]) -> None:
    current_ids = {node.id for node in nodes}
    current_paths = {node.path for node in nodes if node.path is not None}
    stale_ids = [
        node_id
        for node_id, node_type, node_path in connection.execute(
            """
            SELECT id, type, path
            FROM nodes
            WHERE path IS NOT NULL
            """
        )
        if node_path not in current_paths
        or (node_type in {"file", "function", "class", "test"} and node_id not in current_ids)
    ]
    if not stale_ids:
        return

    connection.executemany("DELETE FROM nodes WHERE id = ?", [(node_id,) for node_id in stale_ids])
    connection.executemany(
        "DELETE FROM edges WHERE src = ? OR dst = ?",
        [(node_id, node_id) for node_id in stale_ids],
    )


def rebuild_fts(connection: sqlite3.Connection) -> None:
    connection.execute("DELETE FROM node_fts")
    connection.execute(
        """
        INSERT INTO node_fts (id, name, summary)
        SELECT id, name, COALESCE(summary, '')
        FROM nodes
        """
    )


def iter_project_files() -> Iterable[Path]:
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = normalize_path(path)
        if rel == "project_graph.sqlite":
            continue
        if path.suffix in {".py", ".md"} or rel in {"SYSTEM_DESIGN.md", ".gitignore"}:
            yield path


def parse_python_file(path: Path) -> tuple[list[Node], list[Edge]]:
    rel = normalize_path(path)
    file_id = f"file:{rel}"
    module_name = module_name_for(path)
    nodes: list[Node] = [
        Node(
            id=file_id,
            type="test" if rel.startswith("tests/") else "file",
            name=rel,
            path=rel,
            summary=f"Python {'test ' if rel.startswith('tests/') else ''}file for module {module_name}.",
            meta={"module": module_name},
        )
    ]
    edges: list[Edge] = [Edge(PROJECT_ID, "contains", file_id)]

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        nodes[0] = Node(
            id=file_id,
            type="file",
            name=rel,
            path=rel,
            summary=f"Python file with syntax error: {exc.msg}.",
            meta={"module": module_name, "syntax_error": str(exc)},
        )
        return nodes, edges

    imports = sorted(external_import_roots(tree))
    for dependency in imports:
        dep_id = f"dependency:{dependency}"
        nodes.append(Node(dep_id, "dependency", dependency, summary=f"External dependency imported by {rel}."))
        edges.append(Edge(file_id, "depends_on", dep_id))

    for item in ast.walk(tree):
        if isinstance(item, ast.ClassDef):
            class_id = f"class:{module_name}.{item.name}"
            nodes.append(
                Node(
                    id=class_id,
                    type="class",
                    name=item.name,
                    path=rel,
                    summary=ast.get_docstring(item) or f"Class defined in {rel}.",
                    meta={"module": module_name, "lineno": item.lineno},
                )
            )
            edges.append(Edge(file_id, "contains", class_id))
            if rel.startswith("tests/"):
                edges.append(Edge(class_id, "tested_by", file_id))

        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            owner = class_owner(tree, item)
            qualified = f"{module_name}.{owner}.{item.name}" if owner else f"{module_name}.{item.name}"
            function_id = f"function:{qualified}"
            nodes.append(
                Node(
                    id=function_id,
                    type="function",
                    name=item.name,
                    path=rel,
                    summary=ast.get_docstring(item) or f"Function defined in {rel}.",
                    meta={"module": module_name, "lineno": item.lineno, "async": isinstance(item, ast.AsyncFunctionDef)},
                )
            )
            edges.append(Edge(file_id, "contains", function_id))
            if owner:
                edges.append(Edge(f"class:{module_name}.{owner}", "contains", function_id))
            if rel.startswith("tests/"):
                edges.append(Edge(function_id, "tested_by", file_id))

    return nodes, edges


def external_import_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for item in ast.walk(tree):
        if isinstance(item, ast.Import):
            for alias in item.names:
                root = alias.name.split(".", 1)[0]
                if root not in LOCAL_ROOTS and not is_stdlib(root):
                    roots.add(root)
        elif isinstance(item, ast.ImportFrom) and item.module:
            root = item.module.split(".", 1)[0]
            if item.level == 0 and root not in LOCAL_ROOTS and not is_stdlib(root):
                roots.add(root)
    return roots


def is_stdlib(module_name: str) -> bool:
    return module_name in sys.stdlib_module_names


def class_owner(tree: ast.AST, function: ast.AST) -> str | None:
    for item in ast.walk(tree):
        if not isinstance(item, ast.ClassDef):
            continue
        if function in item.body:
            return item.name
    return None


def static_project_nodes() -> tuple[list[Node], list[Edge]]:
    project_name = PROJECT_ID.removeprefix("project:").replace("_", " ").title()
    nodes = [
        Node(PROJECT_ID, "project", project_name, summary="Project graph root node."),
        Node(
            "feature:project_graph_tooling",
            "feature",
            "Project graph tooling",
            path="scripts",
            summary="Local SQLite project graph updater and query tools for Codex agents.",
        ),
        Node(
            "decision:use_sqlite_project_graph",
            "decision",
            "Use SQLite project graph",
            path="docs/graph-schema.md",
            summary="Store project understanding as queryable nodes and edges in SQLite.",
        ),
    ]
    edges = [
        Edge("feature:project_graph_tooling", "touches", "file:scripts/update_project_graph.py"),
        Edge("feature:project_graph_tooling", "touches", "file:scripts/query_project_graph.py"),
        Edge("decision:use_sqlite_project_graph", "documents", "file:docs/graph-schema.md"),
        Edge("decision:use_sqlite_project_graph", "related_to", "feature:project_graph_tooling"),
    ]
    return nodes, edges


def collect_graph() -> tuple[list[Node], list[Edge]]:
    nodes, edges = static_project_nodes()
    for path in iter_project_files():
        rel = normalize_path(path)
        if path.suffix == ".py":
            file_nodes, file_edges = parse_python_file(path)
            nodes.extend(file_nodes)
            edges.extend(file_edges)
            continue
        file_id = f"file:{rel}"
        nodes.append(Node(file_id, "file", rel, path=rel, summary=f"Project document or config file: {rel}."))
        edges.append(Edge(PROJECT_ID, "contains", file_id))
    return dedupe_nodes(nodes), dedupe_edges(edges)


def dedupe_nodes(nodes: Iterable[Node]) -> list[Node]:
    deduped: dict[str, Node] = {}
    for node in nodes:
        deduped[node.id] = node
    return list(deduped.values())


def dedupe_edges(edges: Iterable[Edge]) -> list[Edge]:
    deduped: dict[tuple[str, str, str], Edge] = {}
    for edge in edges:
        deduped[(edge.src, edge.rel, edge.dst)] = edge
    return list(deduped.values())


def update_graph(graph_path: Path) -> tuple[int, int]:
    nodes, edges = collect_graph()
    with sqlite3.connect(graph_path) as connection:
        ensure_schema(connection)
        upsert_nodes(connection, nodes)
        upsert_edges(connection, edges)
        prune_stale_paths(connection, nodes)
        rebuild_fts(connection)
    return len(nodes), len(edges)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the SQLite project graph.")
    parser.add_argument("--graph", type=Path, default=GRAPH_PATH, help="Path to project_graph.sqlite.")
    args = parser.parse_args()

    node_count, edge_count = update_graph(args.graph)
    print(f"Updated {args.graph} with {node_count} nodes and {edge_count} edges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
