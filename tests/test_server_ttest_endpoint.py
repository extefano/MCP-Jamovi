from __future__ import annotations

from jamovi_mcp import server


def test_jmv_ttestIS_endpoint_success(monkeypatch) -> None:
    monkeypatch.setattr(server, "get_session_dataset_path", lambda _: "/data/demo.omv")
    monkeypatch.setattr(
        server,
        "run_ttest_is",
        lambda *_args, **_kwargs: {
            "analysis": "ttestIS",
            "tables": [{"id": "ttest", "title": "T-Test", "content": [{"stat": 1.23}]}],
            "markdown": "### T-Test",
        },
    )
    monkeypatch.setattr(server, "build_gui_instructions", lambda *_args, **_kwargs: "GUI steps")

    payload = server.jmv_ttestIS(
        session_id="session-123",
        deps=["score"],
        group="group_var",
    )

    assert payload["session_id"] == "session-123"
    assert payload["dataset_path"] == "/data/demo.omv"
    assert payload["analysis"] == "ttestIS"
    assert payload["tables"][0]["id"] == "ttest"
    assert payload["gui_instructions"] == "GUI steps"


def test_jmv_ttestIS_endpoint_accepts_legacy_vars_schema() -> None:
    req = server.TTestISRequest.model_validate(
        {
            "session_id": "s1",
            "vars": ["score"],
            "group": "group_var",
        }
    )
    assert req.deps == ["score"]
