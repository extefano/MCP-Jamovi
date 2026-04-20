from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetMetadata:
    columns: list[dict[str, str]]


class RBridgeError(RuntimeError):
    pass


def _run_rscript(script: str) -> str:
    command = ["Rscript", "-e", script]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RBridgeError(completed.stderr.strip() or "Rscript execution failed")
    return completed.stdout.strip()


def validate_r_environment() -> None:
    script = "suppressPackageStartupMessages({ library(jmv); library(jmvReadWrite) }); cat('ok')"
    output = _run_rscript(script)
    if output != "ok":
        raise RBridgeError("R environment validation failed")


def get_dataset_info(dataset_path: str) -> DatasetMetadata:
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(dataset_path)

    script = f"""
    suppressPackageStartupMessages({{
      library(jmvReadWrite)
      data <- read_omv({json.dumps(str(path))})
      result <- lapply(names(data), function(name) {{
        column <- data[[name]]
        list(name = name, type = class(column)[1])
      }})
      cat(jsonlite::toJSON(result, auto_unbox = TRUE))
    }})
    """
    output = _run_rscript(script)
    columns = json.loads(output)
    return DatasetMetadata(columns=columns)


def run_descriptives(dataset_path: str, vars: list[str]) -> dict:
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(dataset_path)

    vars_json = json.dumps(vars)
    script = f"""
    suppressPackageStartupMessages({{
      library(jmv)
      library(jmvReadWrite)
      data <- read_omv({json.dumps(str(path))})
      result <- descriptives(data = data, vars = c({', '.join(json.dumps(v) for v in vars)}))
      tables <- list()
      if (!is.null(result$descriptives)) {{
        tables$descriptives <- result$descriptives$asDF
      }}
      payload <- list(
        analysis = "descriptives",
        vars = {vars_json},
        tables = tables
      )
      cat(jsonlite::toJSON(payload, auto_unbox = TRUE, null = "null", dataframe = "rows"))
    }})
    """
    output = _run_rscript(script)
    return json.loads(output)
