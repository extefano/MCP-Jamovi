from __future__ import annotations

import time

import pytest

from jamovi_mcp import r_bridge


@pytest.fixture(autouse=True)
def clear_session_store() -> None:
    r_bridge._SESSION_STORE.clear()
    yield
    r_bridge._SESSION_STORE.clear()


def test_load_dataset_to_memory_returns_session_id_and_path(tmp_path) -> None:
    dataset = tmp_path / "demo.omv"
    dataset.write_text("placeholder", encoding="utf-8")

    session_id = r_bridge.load_dataset_to_memory(str(dataset))
    resolved = r_bridge.get_session_dataset_path(session_id)

    assert isinstance(session_id, str)
    assert len(session_id) > 0
    assert resolved == str(dataset)


def test_release_session_removes_mapping(tmp_path) -> None:
    dataset = tmp_path / "demo.omv"
    dataset.write_text("placeholder", encoding="utf-8")

    session_id = r_bridge.load_dataset_to_memory(str(dataset))
    assert r_bridge.release_session(session_id) is True
    assert r_bridge.release_session(session_id) is False

    with pytest.raises(r_bridge.RBridgeError):
        r_bridge.get_session_dataset_path(session_id)


def test_cleanup_expires_inactive_sessions(tmp_path, monkeypatch) -> None:
    dataset = tmp_path / "demo.omv"
    dataset.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(r_bridge, "SESSION_TTL_SECONDS", 0)

    session_id = r_bridge.load_dataset_to_memory(str(dataset))
    time.sleep(0.01)
    removed = r_bridge.cleanup_expired_sessions()

    assert removed >= 1
    with pytest.raises(r_bridge.RBridgeError):
        r_bridge.get_session_dataset_path(session_id)
