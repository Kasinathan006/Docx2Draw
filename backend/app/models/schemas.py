"""
Pydantic request/response schemas for the Doc2Draw API (guide §5.2).

`JobStatusEnum` is the coarse public status. Internally the worker also tracks
a finer-grained `stage` (parsing → ai_structuring → compiling) which is surfaced
as an extra field for richer progress UIs.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobStatusEnum(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class JobStage(str, Enum):
    QUEUED = "queued"
    PARSING = "parsing"
    EXTRACTING_MEDIA = "extracting_media"
    AI_STRUCTURING = "ai_structuring"
    COMPILING = "compiling"
    DONE = "done"
    ERROR = "error"


class ProjectUploadResponse(BaseModel):
    project_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerifyKeyRequest(BaseModel):
    api_key: str

class VerifyKeyResponse(BaseModel):
    valid: bool
    error: Optional[str] = None

class GenerateRequest(BaseModel):
    project_id: str
    title: Optional[str] = None
    columns: int = Field(default=3, ge=1, le=6)
    layout_style: str = Field(default="multi_column_grid")
    extract_screenshots: bool = True
    ai_model_provider: str = Field(default="rule_based")
    api_key: Optional[str] = None


class GenerateResponse(BaseModel):
    job_id: str
    project_id: str
    status: JobStatusEnum
    estimated_time_sec: int = 30


class JobStatusResponse(BaseModel):
    job_id: str
    project_id: str
    status: JobStatusEnum
    stage: JobStage = JobStage.QUEUED
    progress: int = Field(default=0, ge=0, le=100)
    message: str = ""
    result_available: bool = False
    chapters_extracted: int = 0
    error_message: Optional[str] = None


class ExcalidrawResponse(BaseModel):
    project_id: str
    title: str = ""
    type: str = "excalidraw"
    version: int = 2
    source: str = "https://doc2draw.ai"
    elements: List[Dict[str, Any]]
    appState: Dict[str, Any]
    files: Dict[str, Any]


class UserProfileResponse(BaseModel):
    id: str
    email: Optional[str] = None
    subscription_tier: str = "free"
    subscription_status: str = "active"
    monthly_upload_count: int = 0
    monthly_quota: int = 3
    authenticated: bool = False
