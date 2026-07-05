"""
Job status store.

Two interchangeable backends with the same interface:
  * ``JobStore``      — thread-safe in-memory (single-process, default).
  * ``RedisJobStore`` — shared across processes/containers (used automatically
    when ``REDIS_URL`` is configured, so the Celery worker and the API server
    see the same job state).
"""
import json
import threading
from dataclasses import asdict, dataclass, fields as dataclass_fields
from typing import Dict, Optional

from ..config import settings


@dataclass
class JobState:
    job_id: str
    project_id: str
    status: str = "queued"          # coarse: queued|processing|done|error
    stage: str = "queued"           # fine: parsing|ai_structuring|compiling...
    progress: int = 0
    message: str = "Queued for processing"
    chapters_extracted: int = 0
    error_message: Optional[str] = None


class JobStore:
    """In-memory store (single process)."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobState] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, project_id: str) -> JobState:
        with self._lock:
            state = JobState(job_id=job_id, project_id=project_id)
            self._jobs[job_id] = state
            return state

    def update(self, job_id: str, **fields) -> None:
        with self._lock:
            state = self._jobs.get(job_id)
            if state is None:
                return
            for k, v in fields.items():
                setattr(state, k, v)

    def get(self, job_id: str) -> Optional[JobState]:
        with self._lock:
            return self._jobs.get(job_id)


class RedisJobStore:
    """Redis-backed store shared across the API and Celery worker containers."""

    _PREFIX = "doc2draw:job:"
    _TTL = 86400  # 24h

    def __init__(self, redis_url: str) -> None:
        import redis  # local import so redis is only needed when configured

        self._r = redis.from_url(redis_url, decode_responses=True)
        self._field_names = {f.name for f in dataclass_fields(JobState)}

    def _key(self, job_id: str) -> str:
        return f"{self._PREFIX}{job_id}"

    def create(self, job_id: str, project_id: str) -> JobState:
        state = JobState(job_id=job_id, project_id=project_id)
        self._r.set(self._key(job_id), json.dumps(asdict(state)), ex=self._TTL)
        return state

    def update(self, job_id: str, **fields) -> None:
        raw = self._r.get(self._key(job_id))
        if raw is None:
            return
        data = json.loads(raw)
        for k, v in fields.items():
            if k in self._field_names:
                data[k] = v
        self._r.set(self._key(job_id), json.dumps(data), ex=self._TTL)

    def get(self, job_id: str) -> Optional[JobState]:
        raw = self._r.get(self._key(job_id))
        if raw is None:
            return None
        data = json.loads(raw)
        return JobState(**{k: data.get(k) for k in self._field_names})


def _build_store():
    if settings.celery_enabled:
        try:
            return RedisJobStore(settings.redis_url)
        except Exception:
            # Redis client unavailable -> safe local fallback.
            return JobStore()
    return JobStore()


# Module-level singleton (chosen once at import time).
job_store = _build_store()
