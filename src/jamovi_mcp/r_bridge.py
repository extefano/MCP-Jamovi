from __future__ import annotations

import json
import os
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TABLE_JSON_LIMIT_BYTES = 2 * 1024 * 1024
SESSION_TTL_SECONDS = int(os.environ.get("JAMOVI_SESSION_TTL_SECONDS", "1800"))


@dataclass
class SessionHandle:
    dataset_path: str
    created_at: float
    last_access_at: float


@dataclass(frozen=True)
class DatasetMetadata:
    columns: list[dict[str, str]]


@dataclass(frozen=True)
class BridgeMappedError:
    code: int
    type: str
    message: str
    suggested_action: str
    r_pattern: str


class RBridgeError(RuntimeError):
    pass


class AnalysisExecutionError(RuntimeError):
    def __init__(self, mapped: BridgeMappedError):
        super().__init__(mapped.message)
        self.mapped = mapped

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.mapped.code,
            "type": self.mapped.type,
            "message": self.mapped.message,
            "suggested_action": self.mapped.suggested_action,
            "r_pattern": self.mapped.r_pattern,
        }


session_store: dict[str, SessionHandle] = {}
session_store_lock = threading.Lock()

# Backward-compatible aliases for existing tests/imports.
_SESSION_STORE = session_store
_SESSION_LOCK = session_store_lock


def _cleanup_expired_sessions_unlocked(now_ts: float) -> int:
    expired = [
        sid
        for sid, handle in _SESSION_STORE.items()
        if (now_ts - handle.last_access_at) > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        del _SESSION_STORE[sid]
    return len(expired)


def cleanup_expired_sessions() -> int:
    now_ts = time.time()
    with session_store_lock:
        return _cleanup_expired_sessions_unlocked(now_ts)


def load_dataset_to_memory(dataset_path: str) -> str:
    # Current bridge runs one R subprocess per call. We keep a Python-side
    # session map to avoid re-sending dataset path state from clients.
    path = _ensure_exists(dataset_path)
    session_id = uuid.uuid4().hex
    now_ts = time.time()
    with session_store_lock:
        _cleanup_expired_sessions_unlocked(now_ts)
        session_store[session_id] = SessionHandle(
            dataset_path=str(path),
            created_at=now_ts,
            last_access_at=now_ts,
        )
    return session_id


def tool_load_dataset(file_path: str) -> str:
    return load_dataset_to_memory(file_path)


def get_session_dataset_path(session_id: str) -> str:
    now_ts = time.time()
    with session_store_lock:
        _cleanup_expired_sessions_unlocked(now_ts)
        handle = session_store.get(session_id)
        if handle is None:
            raise RBridgeError(f"Session no encontrada o expirada: {session_id}")
        handle.last_access_at = now_ts
        return handle.dataset_path


def release_session(session_id: str) -> bool:
    with session_store_lock:
        return session_store.pop(session_id, None) is not None


def _map_r_error(stderr: str) -> BridgeMappedError | None:
    lowered = stderr.lower()
    patterns = [
        (
            "singular matrix",
            BridgeMappedError(
                code=-32602,
                type="DataError",
                message="Colinealidad extrema detectada en el modelo.",
                suggested_action="Elimina variables redundantes antes de reintentar.",
                r_pattern="singular matrix",
            ),
        ),
        (
            "must have exactly 2 levels",
            BridgeMappedError(
                code=-32602,
                type="DataError",
                message="La variable de agrupacion requiere exactamente 2 niveles para un T-Test.",
                suggested_action="Usa ANOVA para mas de 2 niveles.",
                r_pattern="must have exactly 2 levels",
            ),
        ),
        (
            "cannot be constant",
            BridgeMappedError(
                code=-32602,
                type="VarianceError",
                message="La variable seleccionada no tiene varianza.",
                suggested_action="Selecciona otra variable dependiente o filtra correctamente.",
                r_pattern="cannot be constant",
            ),
        ),
        (
            "missing values in 'x'",
            BridgeMappedError(
                code=-32602,
                type="MissingDataError",
                message="Se detectaron valores perdidos en la variable analizada.",
                suggested_action="Filtra NA o cambia la politica de exclusion de casos.",
                r_pattern="missing values in 'x'",
            ),
        ),
        (
            "is not a factor",
            BridgeMappedError(
                code=-32602,
                type="DataTypeError",
                message="La variable indicada debe ser nominal u ordinal.",
                suggested_action="Convierte la variable a factor en jamovi o selecciona una variable categorica.",
                r_pattern="is not a factor",
            ),
        ),
        (
            "not enough observations",
            BridgeMappedError(
                code=-32602,
                type="SampleSizeError",
                message="N insuficiente para el analisis solicitado.",
                suggested_action="Aumenta la muestra o reduce complejidad del analisis.",
                r_pattern="not enough observations",
            ),
        ),
    ]
    for pattern, mapped in patterns:
        if pattern in lowered:
            return mapped
    return None


def _run_rscript(script: str) -> str:
    command = ["Rscript", "-e", script]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Rscript execution failed"
        mapped = _map_r_error(stderr)
        if mapped is not None:
            raise AnalysisExecutionError(mapped)
        raise RBridgeError(stderr)
    return completed.stdout.strip()


def validate_r_environment() -> None:
    script = "suppressPackageStartupMessages({ library(jmv); library(jmvReadWrite) }); cat('ok')"
    output = _run_rscript(script)
    if output != "ok":
        raise RBridgeError("R environment validation failed")


def _ensure_exists(dataset_path: str) -> Path:
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(dataset_path)
    return path


def _render_markdown_table(table: dict[str, Any]) -> str:
    rows = table.get("content") or []
    title = table.get("title") or table.get("id") or "Tabla"
    if not rows:
        return f"### {title}\n\n(Sin filas)"

    headers = list(rows[0].keys())
    lines = [
        f"### {title}",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        values = [str(row.get(h, "")) for h in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _truncate_table_content(table: dict[str, Any]) -> None:
    content = table.get("content")
    if not isinstance(content, list):
        table["truncated"] = False
        table["original_size_bytes"] = 0
        return

    original_size = len(json.dumps(content, ensure_ascii=False).encode("utf-8"))
    table["original_size_bytes"] = original_size
    table["truncated"] = False
    if original_size <= TABLE_JSON_LIMIT_BYTES:
        return

    rows = content
    while rows and len(json.dumps(rows, ensure_ascii=False).encode("utf-8")) > TABLE_JSON_LIMIT_BYTES:
        rows = rows[: max(1, len(rows) // 2)]

    table["content"] = rows
    table["truncated"] = True


def _enrich_result_payload(payload: dict[str, Any]) -> dict[str, Any]:
    tables = payload.get("tables") or []
    if not isinstance(tables, list):
        payload["tables"] = []
        payload["markdown"] = ""
        return payload

    markdown_blocks: list[str] = []
    for table in tables:
        _truncate_table_content(table)
        markdown_blocks.append(_render_markdown_table(table))
    payload["markdown"] = "\n\n".join(markdown_blocks)
    return payload


def get_dataset_info(dataset_path: str) -> DatasetMetadata:
    path = _ensure_exists(dataset_path)

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


def get_dataset_columns(dataset_path: str) -> set[str]:
    metadata = get_dataset_info(dataset_path)
    return {col["name"] for col in metadata.columns}


def validate_columns_exist(dataset_path: str, columns: list[str]) -> None:
    existing = get_dataset_columns(dataset_path)
    missing = [c for c in columns if c not in existing]
    if missing:
        raise RBridgeError(f"Columnas no encontradas en el dataset: {', '.join(missing)}")


def get_group_levels_count(dataset_path: str, group: str) -> int:
    path = _ensure_exists(dataset_path)
    script = f"""
    suppressPackageStartupMessages({{
      library(jmvReadWrite)
      data <- read_omv({json.dumps(str(path))})
      if (!({json.dumps(group)} %in% names(data))) {{
        stop('group column not found')
      }}
      g <- data[[{json.dumps(group)}]]
      n <- length(unique(stats::na.omit(g)))
      cat(as.character(n))
    }})
    """
    out = _run_rscript(script)
    return int(out)


def _run_jmv_analysis(dataset_path: str, analysis_name: str, r_call: str) -> dict[str, Any]:
    path = _ensure_exists(dataset_path)

    script = f"""
    suppressPackageStartupMessages({{
      library(jmv)
      library(jmvReadWrite)
      library(jsonlite)
      data <- read_omv({json.dumps(str(path))})

      extract_tables <- function(res) {{
        tables <- list()
        items <- NULL

        items <- tryCatch(res$items, error=function(e) NULL)
        if (is.null(items)) {{
          items <- tryCatch(res$results$items, error=function(e) NULL)
        }}

        if (!is.null(items)) {{
          for (nm in names(items)) {{
            item <- items[[nm]]
            df <- tryCatch(item$asDF, error=function(e) NULL)
            if (!is.null(df)) {{
              notes <- tryCatch(item$notes, error=function(e) NULL)
              title <- tryCatch(item$title, error=function(e) nm)
              if (is.null(title) || length(title) == 0) {{
                title <- nm
              }}
              tables[[length(tables) + 1]] <- list(
                id = nm,
                title = as.character(title)[1],
                content = df,
                footnotes = if (is.null(notes)) character() else as.character(unlist(notes))
              )
            }}
          }}
        }}

        if (length(tables) == 0) {{
          fallback_df <- tryCatch(res$descriptives$asDF, error=function(e) NULL)
          if (!is.null(fallback_df)) {{
            tables[[1]] <- list(
              id = 'descriptives',
              title = 'Descriptives',
              content = fallback_df,
              footnotes = character()
            )
          }}
        }}

        return(tables)
      }}

      res <- {r_call}
      payload <- list(
        analysis = {json.dumps(analysis_name)},
        tables = extract_tables(res)
      )
      cat(jsonlite::toJSON(payload, auto_unbox = TRUE, null = 'null', dataframe = 'rows'))
    }})
    """
    raw = _run_rscript(script)
    payload = json.loads(raw)
    return _enrich_result_payload(payload)


def run_descriptives(dataset_path: str, vars: list[str]) -> dict[str, Any]:
    validate_columns_exist(dataset_path, vars)
    r_call = f"descriptives(data = data, vars = c({', '.join(json.dumps(v) for v in vars)}))"
    return _run_jmv_analysis(dataset_path, "descriptives", r_call)


def run_ttest_is(
    dataset_path: str,
    vars: list[str],
    group: str,
    welchs: bool,
    mann: bool,
    norm: bool,
    eqv: bool,
) -> dict[str, Any]:
    validate_columns_exist(dataset_path, [*vars, group])
    levels = get_group_levels_count(dataset_path, group)
    if levels != 2:
        raise AnalysisExecutionError(
            BridgeMappedError(
                code=-32602,
                type="DataError",
                message="La variable de agrupacion requiere exactamente 2 niveles para un T-Test.",
                suggested_action="Usa ANOVA para mas de 2 niveles.",
                r_pattern="must have exactly 2 levels",
            )
        )

    r_call = (
        "ttestIS(data = data, "
        f"vars = c({', '.join(json.dumps(v) for v in vars)}), "
        f"group = {json.dumps(group)}, "
        f"welchs = {str(welchs).upper()}, "
        f"mann = {str(mann).upper()}, "
        f"norm = {str(norm).upper()}, "
        f"eqv = {str(eqv).upper()})"
    )
    return _run_jmv_analysis(dataset_path, "ttestIS", r_call)


def run_corr_matrix(
    dataset_path: str,
    vars: list[str],
    pearson: bool,
    spearman: bool,
    sig: bool,
) -> dict[str, Any]:
    validate_columns_exist(dataset_path, vars)
    r_call = (
        "corrMatrix(data = data, "
        f"vars = c({', '.join(json.dumps(v) for v in vars)}), "
        f"pearson = {str(pearson).upper()}, "
        f"spearman = {str(spearman).upper()}, "
        f"sig = {str(sig).upper()})"
    )
    return _run_jmv_analysis(dataset_path, "corrMatrix", r_call)
