"""
Backend configuration (Pydantic BaseSettings).

Every external integration (Supabase, Redis/Celery, Stripe, S3) is OPTIONAL.
When its credentials are absent the app degrades gracefully to local, in-process
behaviour so the whole stack runs with zero external infrastructure.
"""
import sys
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Make the doc2draw core package importable without installation ----------
# backend/app/config.py -> repo root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---------------------------------------------------------------
    app_name: str = "Doc2Draw AI API"
    version: str = "1.0.0"

    # --- Storage (local filesystem by default) -----------------------------
    storage_root: Path = REPO_ROOT / "backend" / "storage"
    max_upload_mb: int = 512
    free_tier_max_upload_mb: int = 50
    free_tier_monthly_quota: int = 3

    # --- CORS --------------------------------------------------------------
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,*"

    # --- Background processing --------------------------------------------
    workers: int = 2
    redis_url: Optional[str] = None  # e.g. redis://localhost:6379/0

    # --- Supabase (auth + storage + db) -----------------------------------
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None

    # --- Database ----------------------------------------------------------
    database_url: Optional[str] = None

    # --- Stripe ------------------------------------------------------------
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_price_pro: Optional[str] = None
    stripe_price_team: Optional[str] = None

    # --- Cloud object storage (S3 / R2) -----------------------------------
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # --- File type policy --------------------------------------------------
    allowed_extensions: List[str] = [
        ".docx", ".pdf", ".txt", ".md", ".mp4", ".mov", ".avi", ".mkv", ".webm",
        ".png", ".jpg", ".jpeg",
    ]
    video_extensions: List[str] = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    image_extensions: List[str] = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]

    # --- Derived paths -----------------------------------------------------
    @property
    def upload_dir(self) -> Path:
        return self.storage_root / "uploads"

    @property
    def output_dir(self) -> Path:
        return self.storage_root / "outputs"

    @property
    def screenshot_dir(self) -> Path:
        return self.storage_root / "screenshots"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # --- Feature flags (True only when configured) -------------------------
    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @property
    def auth_enabled(self) -> bool:
        return bool(self.supabase_jwt_secret)

    @property
    def db_enabled(self) -> bool:
        return bool(self.database_url)

    @property
    def stripe_enabled(self) -> bool:
        return bool(self.stripe_secret_key and self.stripe_webhook_secret)

    @property
    def s3_enabled(self) -> bool:
        return bool(self.s3_bucket and self.aws_access_key_id)

    @property
    def celery_enabled(self) -> bool:
        return bool(self.redis_url)

    def ensure_dirs(self) -> None:
        for d in (self.upload_dir, self.output_dir, self.screenshot_dir):
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
