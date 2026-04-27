from __future__ import annotations

from dataclasses import dataclass

from .yaml_reader import extract_control_titles, infer_menu_path, load_ui_yaml


@dataclass(frozen=True)
class ToolGuide:
    menu_path: str
    param_map: dict[str, str]


GUIDE_MAP: dict[str, ToolGuide] = {
    "jmv_descriptives": ToolGuide(
        menu_path="Analyses -> Exploration -> Descriptives",
        param_map={
            "vars": "Variables",
            "splitBy": "Split by",
            "freq": "Frequency tables",
        },
    ),
    "jmv_ttestIS": ToolGuide(
        menu_path="Analyses -> T-Tests -> Independent Samples T-Test",
        param_map={
            "vars": "Dependent Variables",
            "group": "Grouping Variable",
            "welchs": "Welch's",
            "norm": "Normality test",
            "eqv": "Equality of variances test",
        },
    ),
    "jmv_corrMatrix": ToolGuide(
        menu_path="Analyses -> Regression -> Correlation Matrix",
        param_map={
            "vars": "Variables",
            "pearson": "Pearson",
            "spearman": "Spearman",
            "sig": "Significance",
        },
    ),
}


def build_gui_instructions(tool_name: str, params: dict) -> str:
    yaml_tree = load_ui_yaml(tool_name)
    yaml_titles = extract_control_titles(yaml_tree) if yaml_tree is not None else {}

    guide = GUIDE_MAP.get(tool_name)
    if guide is None and not yaml_titles:
        return "No hay guia GUI disponible para esta herramienta."

    menu_path = infer_menu_path(yaml_tree) if yaml_tree is not None else None
    if not menu_path and guide is not None:
        menu_path = guide.menu_path
    if not menu_path:
        menu_path = "Analyses"

    static_param_map = guide.param_map if guide is not None else {}

    def resolve_label(key: str, default_label: str) -> str:
        if key in yaml_titles:
            return yaml_titles[key]
        if key in static_param_map:
            return static_param_map[key]
        return default_label

    lines: list[str] = [
        "Para replicar este analisis en la aplicacion de escritorio jamovi:",
        f"Haga clic en el menu {menu_path}.",
    ]

    vars_value = params.get("vars")
    vars_label = resolve_label("vars", "Variables")
    if vars_value and vars_label:
        if isinstance(vars_value, list):
            joined = ", ".join(str(v) for v in vars_value)
        else:
            joined = str(vars_value)
        lines.append(f"Arrastre las variables {joined} al panel de {vars_label}.")

    group_value = params.get("group")
    group_label = resolve_label("group", "Grouping Variable")
    if group_value and group_label:
        lines.append(f"Arrastre la variable {group_value} al panel {group_label}.")

    for key, value in params.items():
        if key in {"vars", "group", "dataset_path"}:
            continue
        if isinstance(value, bool) and value:
            label = resolve_label(key, key)
            if label:
                lines.append(f"Configure {label} activando la opcion {value}.")

    return " ".join(lines)
