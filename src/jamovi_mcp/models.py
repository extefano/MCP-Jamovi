from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class BaseAnalysisModel(BaseModel):
    dataset_path: str = Field(min_length=1)


class DatasetInfoRequest(BaseAnalysisModel):
    pass


class DescriptivesRequest(BaseAnalysisModel):
    vars: List[str] = Field(min_length=1)


class TTestISRequest(BaseAnalysisModel):
    vars: List[str] = Field(min_length=1)
    group: str = Field(min_length=1)
    welchs: bool = True
    mann: bool = False
    norm: bool = True
    eqv: bool = True


class CorrMatrixRequest(BaseAnalysisModel):
    vars: List[str] = Field(min_length=1)
    pearson: bool = True
    spearman: bool = False
    sig: bool = False
