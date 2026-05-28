#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = PROJECT_ROOT / "project_graph.sqlite"


def connect(graph_path: Path) -> sqlite3.Connection:
    if not graph_path.exists():
        raise FileNotFoundError(f"Project graph not found: {graph_path}")
    return sqlite3.connect(graph_path)


def search_nodes(connection: sqlite3.Connection, query: str, limit: int) -> list[tuple[str, str, str, str | None]]:
    sql = """
        SELECT nodes.id, nodes.type, nodes.name, nodes.path
        FROM node_fts
        JOIN nodes ON nodes.id = node_fts.id
        WHERE node_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """
    return list(connection.execute(sql, (query, limit)))


def related_edges(connection: sqlite3.Connection, node_id: str, limit: int) -> list[tuple[str, str, str]]:
    sql = """
        SELECT src, rel, dst
        FROM edges
        WHERE src = ? OR dst = ?
        ORDER BY src, rel, dst
        LIMIT ?
    """
    return list(connection.execute(sql, (node_id, node_id, limit)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the project graph.")
    parser.add_argument("query", help="FTS query or exact node id.")
    parser.add_argument("--graph", type=Path, default=GRAPH_PATH, help="Path to project_graph.sqlite.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum rows to print.")
    parser.add_argument("--edges", action="store_true", help="Show edges for an exact node id.")
    args = parser.parse_args()

    with connect(args.graph) as connection:
        if args.edges:
            for src, rel, dst in related_edges(connection, args.query, args.limit):
                print(f"{src} --{rel}-> {dst}")
            return 0

        for node_id, node_type, name, path in search_nodes(connection, args.query, args.limit):
            suffix = f" ({path})" if path else ""
            print(f"{node_id}\t{node_type}\t{name}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
