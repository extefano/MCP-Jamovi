from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .gui_translator import build_gui_instructions
from .models import (
    CorrMatrixRequest,
    DatasetInfoRequest,
    DescriptivesRequest,
    LoadDatasetRequest,
    TTestISRequest,
)
from .r_bridge import (
    AnalysisExecutionError,
    cleanup_expired_sessions,
    get_dataset_info,
    get_session_dataset_path,
    load_dataset_to_memory,
    release_session,
    run_corr_matrix,
    run_descriptives,
    run_ttest_is,
    validate_r_environment,
)


APP_NAME = "jamovi_mcp"
DATA_ROOT = Path(os.environ.get("JAMOVI_DATA_ROOT", "/data"))
mcp = FastMCP(APP_NAME)


def _error_payload(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, AnalysisExecutionError):
        return {"error": exc.to_dict()}
    return {
        "error": {
            "code": -32000,
            "type": "ServerError",
            "message": str(exc),
            "suggested_action": "Revise los parametros de entrada e intente nuevamente.",
        }
    }


def _resolve_dataset_path(dataset_path: str) -> Path:
    path = Path(dataset_path)
    if path.is_absolute():
        if path == DATA_ROOT or DATA_ROOT in path.parents:
            return path
        raise ValueError("dataset_path must point inside the mounted data root")
    return DATA_ROOT / dataset_path


@mcp.tool()
def tool_get_dataset_info(dataset_path: str) -> dict:
    try:
        request = DatasetInfoRequest.model_validate({"dataset_path": dataset_path})
        dataset_path = _resolve_dataset_path(request.dataset_path)
        metadata = get_dataset_info(str(dataset_path))
        return {
            "dataset_path": str(dataset_path),
            "columns": metadata.columns,
        }
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def tool_load_dataset_to_memory(dataset_path: str) -> dict:
    try:
        request = LoadDatasetRequest.model_validate({"dataset_path": dataset_path})
        dataset_path = _resolve_dataset_path(request.dataset_path)
        session_id = load_dataset_to_memory(str(dataset_path))
        return {
            "dataset_path": str(dataset_path),
            "session_id": session_id,
            "ttl_seconds": int(os.environ.get("JAMOVI_SESSION_TTL_SECONDS", "1800")),
        }
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def tool_release_session(session_id: str) -> dict:
    try:
        released = release_session(session_id)
        return {
            "session_id": session_id,
            "released": released,
        }
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def tool_cleanup_sessions() -> dict:
    try:
        deleted = cleanup_expired_sessions()
        return {"expired_sessions_removed": deleted}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def tool_run_descriptives(session_id: str, vars: list[str]) -> dict:
    try:
        request = DescriptivesRequest.model_validate({"session_id": session_id, "vars": vars})
        dataset_path = get_session_dataset_path(request.session_id)
        payload = run_descriptives(dataset_path, request.vars)
        payload["dataset_path"] = dataset_path
        payload["session_id"] = request.session_id
        payload["gui_instructions"] = build_gui_instructions(
            "jmv_descriptives",
            {
                "session_id": request.session_id,
                "vars": request.vars,
            },
        )
        return payload
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def jmv_ttestIS(
    session_id: str,
    deps: list[str],
    group: str,
    welchs: bool = True,
    mann: bool = False,
    norm: bool = True,
    eqv: bool = True,
) -> dict:
    try:
        request = TTestISRequest.model_validate(
            {
                "session_id": session_id,
                "deps": deps,
                "group": group,
                "welchs": welchs,
                "mann": mann,
                "norm": norm,
                "eqv": eqv,
            }
        )
        dataset_path = get_session_dataset_path(request.session_id)
        payload = run_ttest_is(
            dataset_path,
            request.deps,
            request.group,
            request.welchs,
            request.mann,
            request.norm,
            request.eqv,
        )
        payload["dataset_path"] = dataset_path
        payload["session_id"] = request.session_id
        payload["gui_instructions"] = build_gui_instructions(
            "jmv_ttestIS",
            {
                "session_id": request.session_id,
                "vars": request.deps,
                "group": request.group,
                "welchs": request.welchs,
                "norm": request.norm,
                "eqv": request.eqv,
            },
        )
        return payload
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def jmv_corrMatrix(
    session_id: str,
    vars: list[str],
    pearson: bool = True,
    spearman: bool = False,
    sig: bool = False,
) -> dict:
    try:
        request = CorrMatrixRequest.model_validate(
            {
                "session_id": session_id,
                "vars": vars,
                "pearson": pearson,
                "spearman": spearman,
                "sig": sig,
            }
        )
        dataset_path = get_session_dataset_path(request.session_id)
        payload = run_corr_matrix(
            dataset_path,
            request.vars,
            request.pearson,
            request.spearman,
            request.sig,
        )
        payload["dataset_path"] = dataset_path
        payload["session_id"] = request.session_id
        payload["gui_instructions"] = build_gui_instructions(
            "jmv_corrMatrix",
            {
                "session_id": request.session_id,
                "vars": request.vars,
                "pearson": request.pearson,
                "spearman": request.spearman,
                "sig": request.sig,
            },
        )
        return payload
    except Exception as exc:
        return _error_payload(exc)


def main() -> None:
    validate_r_environment()
    mcp.run()


if __name__ == "__main__":
    main()
