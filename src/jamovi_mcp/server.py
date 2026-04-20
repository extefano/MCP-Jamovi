from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .models import DatasetInfoRequest, DescriptivesRequest
from .r_bridge import get_dataset_info, run_descriptives, validate_r_environment


APP_NAME = "jamovi_mcp"
DATA_ROOT = Path(os.environ.get("JAMOVI_DATA_ROOT", "/data"))
mcp = FastMCP(APP_NAME)


def _resolve_dataset_path(dataset_path: str) -> Path:
    path = Path(dataset_path)
    if path.is_absolute():
        if path == DATA_ROOT or DATA_ROOT in path.parents:
            return path
        raise ValueError("dataset_path must point inside the mounted data root")
    return DATA_ROOT / dataset_path


@mcp.tool()
def tool_get_dataset_info(dataset_path: str) -> dict:
    request = DatasetInfoRequest.model_validate({"dataset_path": dataset_path})
    dataset_path = _resolve_dataset_path(request.dataset_path)
    metadata = get_dataset_info(str(dataset_path))
    return {
        "dataset_path": str(dataset_path),
        "columns": metadata.columns,
    }


@mcp.tool()
def tool_run_descriptives(dataset_path: str, vars: list[str]) -> dict:
    request = DescriptivesRequest.model_validate({"dataset_path": dataset_path, "vars": vars})
    dataset_path = _resolve_dataset_path(request.dataset_path)
    payload = run_descriptives(str(dataset_path), request.vars)
    payload["dataset_path"] = str(dataset_path)
    payload["gui_instructions"] = (
        "Para replicar esto en jamovi: Vaya a 'Exploration' -> 'Descriptives' y arrastre las variables "
        f"{', '.join(request.vars)} al cuadro 'Variables'."
    )
    return payload


def main() -> None:
    validate_r_environment()
    mcp.run()


if __name__ == "__main__":
    main()
