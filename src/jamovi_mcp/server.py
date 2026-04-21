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
    TTestISRequest,
)
from .r_bridge import (
    AnalysisExecutionError,
    get_dataset_info,
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
def tool_run_descriptives(dataset_path: str, vars: list[str]) -> dict:
    try:
        request = DescriptivesRequest.model_validate({"dataset_path": dataset_path, "vars": vars})
        dataset_path = _resolve_dataset_path(request.dataset_path)
        payload = run_descriptives(str(dataset_path), request.vars)
        payload["dataset_path"] = str(dataset_path)
        payload["gui_instructions"] = build_gui_instructions(
            "jmv_descriptives",
            {
                "dataset_path": request.dataset_path,
                "vars": request.vars,
            },
        )
        return payload
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def jmv_ttestIS(
    dataset_path: str,
    vars: list[str],
    group: str,
    welchs: bool = True,
    mann: bool = False,
    norm: bool = True,
    eqv: bool = True,
) -> dict:
    try:
        request = TTestISRequest.model_validate(
            {
                "dataset_path": dataset_path,
                "vars": vars,
                "group": group,
                "welchs": welchs,
                "mann": mann,
                "norm": norm,
                "eqv": eqv,
            }
        )
        resolved_path = _resolve_dataset_path(request.dataset_path)
        payload = run_ttest_is(
            str(resolved_path),
            request.vars,
            request.group,
            request.welchs,
            request.mann,
            request.norm,
            request.eqv,
        )
        payload["dataset_path"] = str(resolved_path)
        payload["gui_instructions"] = build_gui_instructions(
            "jmv_ttestIS",
            {
                "dataset_path": request.dataset_path,
                "vars": request.vars,
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
    dataset_path: str,
    vars: list[str],
    pearson: bool = True,
    spearman: bool = False,
    sig: bool = False,
) -> dict:
    try:
        request = CorrMatrixRequest.model_validate(
            {
                "dataset_path": dataset_path,
                "vars": vars,
                "pearson": pearson,
                "spearman": spearman,
                "sig": sig,
            }
        )
        resolved_path = _resolve_dataset_path(request.dataset_path)
        payload = run_corr_matrix(
            str(resolved_path),
            request.vars,
            request.pearson,
            request.spearman,
            request.sig,
        )
        payload["dataset_path"] = str(resolved_path)
        payload["gui_instructions"] = build_gui_instructions(
            "jmv_corrMatrix",
            {
                "dataset_path": request.dataset_path,
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
