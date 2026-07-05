"""
Storage service (guide §5.1 services/storage_service.py).

Default implementation persists to the local filesystem so the stack runs with
zero cloud dependencies. If Supabase Storage is configured, uploaded files are
best-effort mirrored there; failures never break the local flow.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import settings


def upload_path(project_id: str, ext: str) -> Path:
    return settings.upload_dir / f"{project_id}{ext}"


def find_upload(project_id: str) -> Optional[Path]:
    matches = sorted(settings.upload_dir.glob(f"{project_id}.*"))
    return matches[0] if matches else None


def output_path(project_id: str) -> Path:
    return settings.output_dir / f"{project_id}.excalidraw"


def save_upload_bytes(project_id: str, ext: str, data: bytes) -> Path:
    settings.ensure_dirs()
    dest = upload_path(project_id, ext)
    dest.write_bytes(data)
    _mirror_to_supabase(dest, f"uploads/{dest.name}")
    return dest


def save_output(project_id: str, excalidraw: Dict[str, Any]) -> Path:
    settings.ensure_dirs()
    dest = output_path(project_id)
    dest.write_text(json.dumps(excalidraw, indent=2), encoding="utf-8")
    return dest


def load_output(project_id: str) -> Optional[Dict[str, Any]]:
    path = output_path(project_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def output_exists(project_id: str) -> bool:
    return output_path(project_id).exists()


def _mirror_to_supabase(local_path: Path, remote_key: str) -> None:
    """Best-effort upload to Supabase Storage; never raises."""
    if not settings.supabase_enabled:
        return
    try:  # pragma: no cover - requires live Supabase
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        bucket = client.storage.from_("projects")
        bucket.upload(remote_key, str(local_path), {"upsert": "true"})
    except Exception:
        # Cloud mirroring is optional; local copy is the source of truth.
        pass
