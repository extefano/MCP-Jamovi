from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


DEFAULT_UI_YAML_ROOT = Path(os.environ.get("JAMOVI_UI_YAML_ROOT", "/opt/jamovi/modules/jmv"))


def _strip_prefix(analysis_name: str) -> str:
    return analysis_name.removeprefix("jmv_")


def _candidate_filenames(analysis_name: str) -> list[str]:
    base = _strip_prefix(analysis_name)
    lowered = base.lower()
    return [
        f"{base}.u.yaml",
        f"{base}.ui.yaml",
        f"{lowered}.u.yaml",
        f"{lowered}.ui.yaml",
    ]


def resolve_ui_yaml_path(analysis_name: str, yaml_root: Path | None = None) -> Path | None:
    root = yaml_root or DEFAULT_UI_YAML_ROOT
    for filename in _candidate_filenames(analysis_name):
        direct = root / filename
        if direct.exists():
            return direct

        nested = list(root.glob(f"**/{filename}"))
        if nested:
            return nested[0]
    return None


def load_ui_yaml(analysis_name: str, yaml_root: Path | None = None) -> dict[str, Any] | None:
    path = resolve_ui_yaml_path(analysis_name, yaml_root)
    if path is None:
        return None
    with path.open("r", encoding="utf-8") as fh:
        parsed = yaml.safe_load(fh)
    if not isinstance(parsed, dict):
        return None
    return parsed


def extract_control_titles(tree: Any) -> dict[str, str]:
    mapping: dict[str, str] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            name = node.get("name")
            title = node.get("title")
            if isinstance(name, str) and isinstance(title, str) and name.strip() and title.strip():
                mapping[name] = title
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(tree)
    return mapping


def infer_menu_path(tree: dict[str, Any]) -> str | None:
    menu_candidates = [
        tree.get("menu"),
        tree.get("menuTitle"),
        tree.get("title"),
    ]
    for candidate in menu_candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate
    return None
