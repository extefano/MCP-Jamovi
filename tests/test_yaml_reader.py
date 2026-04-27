from __future__ import annotations

from pathlib import Path

from jamovi_mcp.gui_translator import build_gui_instructions
from jamovi_mcp import yaml_reader


def test_extract_control_titles_from_mock_yaml(tmp_path, monkeypatch) -> None:
    module_dir = tmp_path / "jmv"
    module_dir.mkdir(parents=True)
    ui_file = module_dir / "ttestIS.u.yaml"
    ui_file.write_text(
        """
menu: Analyses -> T-Tests -> Independent Samples T-Test
children:
  - type: VariablesListBox
    name: vars
    title: Dependent Variables
  - type: VariablesListBox
    name: group
    title: Grouping Variable
  - type: CheckBox
    name: welchs
    title: Welch's
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(yaml_reader, "DEFAULT_UI_YAML_ROOT", Path(module_dir))

    tree = yaml_reader.load_ui_yaml("jmv_ttestIS")
    assert tree is not None

    titles = yaml_reader.extract_control_titles(tree)
    assert titles["vars"] == "Dependent Variables"
    assert titles["group"] == "Grouping Variable"
    assert titles["welchs"] == "Welch's"


def test_build_gui_instructions_uses_yaml_when_available(tmp_path, monkeypatch) -> None:
    module_dir = tmp_path / "jmv"
    module_dir.mkdir(parents=True)
    ui_file = module_dir / "ttestIS.u.yaml"
    ui_file.write_text(
        """
menu: Analyses -> T-Tests -> Independent Samples T-Test
children:
  - type: VariablesListBox
    name: vars
    title: Dependents
  - type: VariablesListBox
    name: group
    title: Group Selector
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(yaml_reader, "DEFAULT_UI_YAML_ROOT", Path(module_dir))

    message = build_gui_instructions(
        "jmv_ttestIS",
        {
            "vars": ["score"],
            "group": "sexo",
            "welchs": True,
        },
    )

    assert "Independent Samples T-Test" in message
    assert "Dependents" in message
    assert "Group Selector" in message


def test_descriptives_yaml_mock_is_loaded(tmp_path, monkeypatch) -> None:
    module_dir = tmp_path / "jmv"
    module_dir.mkdir(parents=True)
    ui_file = module_dir / "descriptives.u.yaml"
    ui_file.write_text(
        """
menu: Analyses -> Exploration -> Descriptives
children:
  - type: VariablesListBox
    name: vars
    title: Variables
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(yaml_reader, "DEFAULT_UI_YAML_ROOT", Path(module_dir))

    tree = yaml_reader.load_ui_yaml("jmv_descriptives")
    assert tree is not None

    titles = yaml_reader.extract_control_titles(tree)
    assert titles["vars"] == "Variables"
