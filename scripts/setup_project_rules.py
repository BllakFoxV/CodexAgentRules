#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_AGENT_RULES = REPO_ROOT / "example_project_rule" / "AGENTS.md"
GRAPH_SCHEMA = REPO_ROOT / "docs" / "graph-schema.md"
GRAPH_SCRIPTS = (
    REPO_ROOT / "scripts" / "update_project_graph.py",
    REPO_ROOT / "scripts" / "query_project_graph.py",
)
GITIGNORE_BLOCK = """
# Local project graph tooling for Codex agents
project_graph.sqlite
project_graph.sqlite-*
docs/graph-schema.md
scripts/update_project_graph.py
scripts/query_project_graph.py
""".strip()


def project_id_from_path(project_root: Path) -> str:
    name = re.sub(r"[^a-zA-Z0-9_]+", "_", project_root.name).strip("_").lower()
    return f"project:{name or 'project'}"


def detect_local_roots(project_root: Path) -> set[str]:
    roots: set[str] = set()
    skip_dirs = {".git", ".venv", "venv", "env", "__pycache__", "docs", "scripts"}
    for path in project_root.iterdir():
        if path.name in skip_dirs or path.name.startswith("."):
            continue
        if path.is_file() and path.suffix == ".py":
            roots.add(path.stem)
            continue
        if path.is_dir() and any(child.suffix == ".py" for child in path.rglob("*.py")):
            roots.add(path.name)
    return roots or {"tests"}


def format_roots(roots: set[str]) -> str:
    return "{" + ", ".join(repr(root) for root in sorted(roots)) + "}"


def configure_update_script(script_path: Path, project_id: str, local_roots: set[str]) -> None:
    content = script_path.read_text(encoding="utf-8")
    content = re.sub(r'^PROJECT_ID = ".*"$', f'PROJECT_ID = "{project_id}"', content, flags=re.MULTILINE)
    content = re.sub(r"^LOCAL_ROOTS = \{.*\}$", f"LOCAL_ROOTS = {format_roots(local_roots)}", content, flags=re.MULTILINE)
    script_path.write_text(content, encoding="utf-8")


def copy_file(src: Path, dst: Path, *, force: bool) -> bool:
    if dst.exists() and not force:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def append_gitignore(project_root: Path) -> bool:
    gitignore = project_root / ".gitignore"
    current = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    missing = [line for line in GITIGNORE_BLOCK.splitlines() if line and line not in current]
    if not missing:
        return False
    prefix = "" if not current or current.endswith("\n") else "\n"
    gitignore.write_text(f"{current}{prefix}\n{GITIGNORE_BLOCK}\n", encoding="utf-8")
    return True


def install(project_root: Path, *, force: bool, project_id: str | None, local_roots: set[str] | None) -> list[str]:
    project_root = project_root.resolve()
    if not project_root.exists() or not project_root.is_dir():
        raise FileNotFoundError(f"Project root not found: {project_root}")

    installed: list[str] = []
    if copy_file(TEMPLATE_AGENT_RULES, project_root / "AGENTS.md", force=force):
        installed.append("AGENTS.md")

    if copy_file(GRAPH_SCHEMA, project_root / "docs" / "graph-schema.md", force=force):
        installed.append("docs/graph-schema.md")

    copied_update_script = False
    for script in GRAPH_SCRIPTS:
        dst = project_root / "scripts" / script.name
        if copy_file(script, dst, force=force):
            installed.append(f"scripts/{script.name}")
            copied_update_script = copied_update_script or script.name == "update_project_graph.py"

    if copied_update_script:
        resolved_project_id = project_id or project_id_from_path(project_root)
        resolved_roots = local_roots or detect_local_roots(project_root)
        configure_update_script(project_root / "scripts" / "update_project_graph.py", resolved_project_id, resolved_roots)
    if append_gitignore(project_root):
        installed.append(".gitignore")
    return installed


def parse_roots(value: str | None) -> set[str] | None:
    if value is None:
        return None
    roots = {item.strip() for item in value.split(",") if item.strip()}
    return roots or None


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Codex agent rules and local graph tooling into a project.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing AGENTS.md and graph tooling files.")
    parser.add_argument("--project-id", help="Project graph id, e.g. project:waydroidmgr.")
    parser.add_argument("--local-roots", help="Comma-separated local import roots, e.g. core,ui,shared,tests,main.")
    args = parser.parse_args()

    installed = install(
        args.project_root,
        force=args.force,
        project_id=args.project_id,
        local_roots=parse_roots(args.local_roots),
    )
    for item in installed:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
