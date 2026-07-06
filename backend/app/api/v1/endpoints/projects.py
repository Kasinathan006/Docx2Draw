"""
Project endpoints (guide §5.3): upload, generate, status, excalidraw, download.
"""
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from ....config import settings
from ....core.auth import CurrentUser, get_current_user
from ....core.exceptions import NotFoundError, PayloadTooLargeError, UnsupportedMediaError
from ....models.schemas import (
    GenerateRequest,
    GenerateResponse,
    JobStage,
    JobStatusEnum,
    JobStatusResponse,
    ProjectUploadResponse,
    VerifyKeyRequest,
    VerifyKeyResponse,
)
from ....services import storage_service
from ....util import new_id
from ....workers.store import job_store
from ....workers.tasks import dispatch

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/verify-key", response_model=VerifyKeyResponse)
def verify_key(req: VerifyKeyRequest):
    provider = (req.provider or "openai").lower()
    try:
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=req.api_key)
            client.models.list()

        elif provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=req.api_key)
            models = [m for m in genai.list_models()]
            if not models:
                raise ValueError("No models returned — key may be invalid")

        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=req.api_key)
            # Minimal API call — list models (or use a tiny message)
            client.models.list()

        elif provider == "groq":
            from openai import OpenAI
            client = OpenAI(
                api_key=req.api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            client.models.list()

        else:
            return VerifyKeyResponse(valid=False, error=f"Unknown provider: {provider}")

        return VerifyKeyResponse(valid=True)
    except Exception as e:
        err = str(e)
        # Friendly error messages
        if "401" in err or "invalid_api_key" in err.lower() or "authentication" in err.lower():
            err = "Invalid API key — check the key and try again"
        elif "403" in err:
            err = "Access denied — your key may not have permission"
        elif "429" in err:
            err = "Rate limit hit — but your key is valid!"
        return VerifyKeyResponse(valid=False, error=err)




@router.post("/upload", response_model=ProjectUploadResponse)
async def upload_project(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions:
        raise UnsupportedMediaError(
            f"Unsupported file type '{ext}'. Allowed: {settings.allowed_extensions}"
        )

    project_id = new_id("proj")
    dest = storage_service.upload_path(project_id, ext)
    settings.ensure_dirs()

    size = 0
    with open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_bytes:
                out.close()
                dest.unlink(missing_ok=True)
                raise PayloadTooLargeError(
                    f"File exceeds max size of {settings.max_upload_mb} MB"
                )
            out.write(chunk)

    storage_service._mirror_to_supabase(dest, f"uploads/{dest.name}")

    return ProjectUploadResponse(
        project_id=project_id,
        filename=file.filename or dest.name,
        file_type=ext.lstrip("."),
        file_size_bytes=size,
    )


@router.post("/generate", response_model=GenerateResponse)
def generate_project(
    req: GenerateRequest,
    user: CurrentUser = Depends(get_current_user),
):
    upload = storage_service.find_upload(req.project_id)
    if upload is None:
        raise NotFoundError(f"No upload found for project '{req.project_id}'")

    job_id = new_id("job")
    job_store.create(job_id, req.project_id)
    dispatch(
        job_id,
        req.project_id,
        {
            "title": req.title,
            "columns": req.columns,
            "layout_style": req.layout_style,
            "extract_screenshots": req.extract_screenshots,
            "api_key": req.api_key,
            "ai_provider": req.ai_provider,
        },
    )
    return GenerateResponse(
        job_id=job_id,
        project_id=req.project_id,
        status=JobStatusEnum.QUEUED,
        estimated_time_sec=30,
    )


@router.get("/{job_id}/status", response_model=JobStatusResponse)
def job_status(job_id: str):
    state = job_store.get(job_id)
    if state is None:
        raise NotFoundError(f"Job '{job_id}' not found")
    return JobStatusResponse(
        job_id=state.job_id,
        project_id=state.project_id,
        status=JobStatusEnum(state.status),
        stage=JobStage(state.stage),
        progress=state.progress,
        message=state.message,
        result_available=state.status == "done" and storage_service.output_exists(state.project_id),
        chapters_extracted=state.chapters_extracted,
        error_message=state.error_message,
    )


@router.get("/{project_id}/excalidraw")
def get_excalidraw(project_id: str):
    data = storage_service.load_output(project_id)
    if data is None:
        raise NotFoundError(f"No compiled diagram for project '{project_id}' yet")
    # Return the raw Excalidraw document so @excalidraw/excalidraw can load it directly.
    return JSONResponse(content=data)


@router.get("/{project_id}/download")
def download_excalidraw(project_id: str):
    path = storage_service.output_path(project_id)
    if not path.exists():
        raise NotFoundError(f"No compiled diagram for project '{project_id}' yet")
    return FileResponse(path, media_type="application/json", filename=f"{project_id}.excalidraw")
