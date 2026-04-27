from __future__ import annotations

from jamovi_mcp import r_bridge


def test_error_mapping_singular_matrix() -> None:
    mapped = r_bridge._map_r_error("Error in solve.default: singular matrix")
    assert mapped is not None
    assert mapped.code == -32602
    assert mapped.r_pattern == "singular matrix"
    assert "Colinealidad extrema" in mapped.message


def test_error_mapping_two_levels() -> None:
    mapped = r_bridge._map_r_error("grouping variable must have exactly 2 levels")
    assert mapped is not None
    assert mapped.code == -32602
    assert mapped.r_pattern == "must have exactly 2 levels"
    assert "2 niveles" in mapped.message
