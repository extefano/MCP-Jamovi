from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class DatasetInfoRequest(BaseModel):
    dataset_path: str = Field(min_length=1)


class DescriptivesRequest(BaseModel):
    dataset_path: str = Field(min_length=1)
    vars: List[str] = Field(min_length=1)
