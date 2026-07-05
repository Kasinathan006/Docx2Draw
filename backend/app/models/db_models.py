"""
SQLModel database models (guide §5.1 / §7.1).

These mirror the Supabase PostgreSQL DDL in ``supabase/schema.sql``. They are
only used when ``settings.db_enabled`` is true; the app runs fully without a
database (status is kept in an in-memory store). Importing this module never
requires a live DB connection.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlmodel import JSON, Column, Field, SQLModel


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Profile(SQLModel, table=True):
    __tablename__ = "profiles"

    id: str = Field(default_factory=_uuid, primary_key=True)
    email: str = Field(index=True)
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    stripe_customer_id: Optional[str] = Field(default=None, index=True)
    subscription_tier: str = Field(default="free")
    subscription_status: str = Field(default="active")
    monthly_upload_count: int = Field(default=0)
    quota_reset_date: datetime = Field(default_factory=_now)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: str = Field(default_factory=_uuid, primary_key=True)
    user_id: Optional[str] = Field(default=None, index=True)
    title: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    storage_path: str
    status: str = Field(default="queued")
    columns_config: int = Field(default=3)
    layout_style: str = Field(default="multi_column_grid")
    excalidraw_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: str = Field(default_factory=_uuid, primary_key=True)
    project_id: str = Field(index=True)
    status: str = Field(default="queued")
    progress: int = Field(default=0)
    chapters_extracted: int = Field(default=0)
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=_now)
    completed_at: Optional[datetime] = None
