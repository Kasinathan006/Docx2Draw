"""
Doc2Draw FastAPI application entrypoint (guide §5.1 main.py).

Wires together CORS, exception handlers, and the versioned API router. Boots
with zero external infrastructure; Supabase/Redis/Stripe activate automatically
when their environment variables are present.
"""
from fastapi import FastAPI

from .config import settings
from .core.exceptions import register_exception_handlers
from .core.security import configure_cors
from .api.v1.router import api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Turn Word Documents, PDF Notes, and Video Courses into Excalidraw Visual Maps.",
)

configure_cors(app)
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/health", tags=["meta"])
def health():
    return {
        "status": "ok",
        "service": "doc2draw-api",
        "version": settings.version,
        "features": {
            "auth": settings.auth_enabled,
            "database": settings.db_enabled,
            "celery": settings.celery_enabled,
            "stripe": settings.stripe_enabled,
            "supabase_storage": settings.supabase_enabled,
        },
    }


@app.get("/", tags=["meta"])
def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "endpoints": [
            "POST /api/v1/projects/upload",
            "POST /api/v1/projects/generate",
            "GET /api/v1/projects/{job_id}/status",
            "GET /api/v1/projects/{project_id}/excalidraw",
            "GET /api/v1/projects/{project_id}/download",
            "GET /api/v1/users/me",
            "POST /api/v1/webhooks/stripe",
        ],
    }
