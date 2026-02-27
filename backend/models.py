from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field

from . import constants


class ToolName(str, Enum):
    PDF_COMPRESSOR = constants.PDF_COMPRESSOR
    PDF_MERGE = constants.PDF_MERGE
    PDF_SPLIT = constants.PDF_SPLIT
    PDF_TO_WORD = constants.PDF_TO_WORD
    WORD_TO_PDF = constants.WORD_TO_PDF
    IMAGE_TO_PDF = constants.IMAGE_TO_PDF
    PDF_FORM_FILLER = constants.PDF_FORM_FILLER


class ValidationResult(BaseModel):
    filename: str
    size_mb: float
    mime_type: str
    valid: bool
    errors: list[str] = Field(default_factory=list)


class JobCreateRequest(BaseModel):
    tool: ToolName
    input_files: list[str]
    options: dict = Field(default_factory=dict)


class JobStatusResponse(BaseModel):
    id: str
    status: str
    progress: int
    eta_seconds: int = 0


class JobResultResponse(BaseModel):
    id: str
    status: str
    download_url: str
    meta: dict
