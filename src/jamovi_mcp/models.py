from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, model_validator


class DatasetPathModel(BaseModel):
    dataset_path: str = Field(min_length=1)


class DatasetInfoRequest(DatasetPathModel):
    pass


class LoadDatasetRequest(DatasetPathModel):
    pass


class SessionAnalysisModel(BaseModel):
    session_id: str = Field(min_length=1)


class DescriptivesRequest(SessionAnalysisModel):
    vars: List[str] = Field(min_length=1)


class TTestISRequest(SessionAnalysisModel):
    deps: List[str] = Field(min_length=1)
    group: str = Field(min_length=1)
    welchs: bool = True
    mann: bool = False
    norm: bool = True
    eqv: bool = True

    @model_validator(mode="before")
    @classmethod
    def normalize_deps_field(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "deps" not in payload and "vars" in payload:
            payload["deps"] = payload["vars"]
        return payload


class CorrMatrixRequest(SessionAnalysisModel):
    vars: List[str] = Field(min_length=1)
    pearson: bool = True
    spearman: bool = False
    sig: bool = False
