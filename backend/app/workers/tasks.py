"""
Background worker tasks (guide §5.4).

Runs the generation pipeline asynchronously. Uses Celery when `REDIS_URL` is
configured; otherwise falls back to an in-process thread pool so the API works
out of the box with no broker. Both paths share `_run_generation`.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict

from celery import Celery

from ..config import settings
from ..services import generator_service, storage_service
from .store import job_store

logger = logging.getLogger("doc2draw.worker")

# Celery app — broker defaults to the in-memory transport when Redis is absent,
# so importing/constructing it never opens a network connection.
celery_app = Celery(
    "doc2draw_worker",
    broker=settings.redis_url or "memory://",
    backend=settings.redis_url or "cache+memory://",
)
celery_app.conf.update(task_track_started=True, task_serializer="json")

# In-process fallback executor.
_executor = ThreadPoolExecutor(max_workers=settings.workers, thread_name_prefix="doc2draw-job")


def _progress(job_id: str):
    def cb(stage: str, progress: int, message: str) -> None:
        job_store.update(job_id, status="processing", stage=stage, progress=progress, message=message)
        _persist_job(job_id)
    return cb


def _run_generation(job_id: str, project_id: str, config: Dict) -> None:
    """Core work function shared by Celery and the in-process fallback."""
    try:
        job_store.update(job_id, status="processing", stage="parsing", progress=10, message="Starting")
        upload = storage_service.find_upload(project_id)
        if upload is None:
            raise FileNotFoundError(f"No uploaded file for project '{project_id}'")

        excalidraw, chapters = generator_service.run_generation(
            input_path=str(upload),
            title=config.get("title") or "Visual Map",
            columns=int(config.get("columns", 3)),
            extract_screenshots=bool(config.get("extract_screenshots", True)),
            project_id=project_id,
            progress_cb=_progress(job_id),
        )

        storage_service.save_output(project_id, excalidraw)
        job_store.update(
            job_id,
            status="done",
            stage="done",
            progress=100,
            message="Visual map ready",
            chapters_extracted=chapters,
        )
        _persist_job(job_id, completed=True)
    except Exception as exc:  # noqa: BLE001 - surface any failure to the client
        logger.exception("Generation failed for job %s", job_id)
        job_store.update(
            job_id,
            status="error",
            stage="error",
            progress=0,
            message="Processing failed",
            error_message=f"{type(exc).__name__}: {exc}",
        )
        _persist_job(job_id, completed=True)


@celery_app.task(name="doc2draw.process_project_generation", bind=True)
def process_project_generation(self, job_id: str, project_id: str, config: Dict):  # noqa: ANN001
    _run_generation(job_id, project_id, config)


def dispatch(job_id: str, project_id: str, config: Dict) -> None:
    """Queue a generation job on Celery, or run it in-process when no broker."""
    if settings.celery_enabled:
        try:
            process_project_generation.delay(job_id, project_id, config)
            return
        except Exception as exc:  # broker unreachable -> fall back gracefully
            logger.warning("Celery dispatch failed (%s); running in-process", exc)
    _executor.submit(_run_generation, job_id, project_id, config)


def _persist_job(job_id: str, completed: bool = False) -> None:
    """Best-effort DB persistence; a no-op when no database is configured."""
    if not settings.db_enabled:
        return
    try:  # pragma: no cover - requires a live database
        from sqlmodel import Session, create_engine, select
        from ..models.db_models import Job as JobRow

        state = job_store.get(job_id)
        if state is None:
            return
        engine = create_engine(settings.database_url)
        with Session(engine) as session:
            row = session.get(JobRow, job_id)
            if row is None:
                row = JobRow(id=job_id, project_id=state.project_id)
            row.status = state.status
            row.progress = state.progress
            row.chapters_extracted = state.chapters_extracted
            row.error_message = state.error_message
            if completed:
                row.completed_at = datetime.now(timezone.utc)
            session.add(row)
            session.commit()
    except Exception as exc:
        logger.error("DB persistence failed for job %s: %s", job_id, exc)
