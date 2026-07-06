"""
Generator service (guide §5.1 services/generator_service.py).

The single bridge between the FastAPI layer and the Phase 1 `doc2draw` core
package. Runs the full pipeline (parse → structure → layout → compile) and
reports progress through a callback so both the Celery worker and the in-process
fallback can share identical logic.
"""
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from ..config import settings

# doc2draw core (importable because config.py put the repo root on sys.path).
from doc2draw.parsers.docx_parser import parse_docx
from doc2draw.parsers.pdf_parser import parse_pdf
from doc2draw.parsers.media_parser import parse_media
from doc2draw.ai.extractor import extract_diagram_structure
from doc2draw.compiler.excalidraw_compiler import build_excalidraw_dict
from doc2draw.compiler.excalidraw_compiler import validate_excalidraw_dict, ExcalidrawValidationError

# progress_cb(stage: str, progress: int, message: str) -> None
ProgressCb = Optional[Callable[[str, int, str], None]]


def _noop(stage: str, progress: int, message: str) -> None:  # pragma: no cover
    pass


def run_generation(
    input_path: str,
    title: str,
    columns: int = 3,
    extract_screenshots: bool = True,
    project_id: Optional[str] = None,
    progress_cb: ProgressCb = None,
    api_key: Optional[str] = None,
) -> Tuple[Dict, int]:
    """
    Execute the end-to-end generation pipeline.

    Returns ``(excalidraw_dict, chapters_extracted)``. Raises on any failure so
    the caller can mark the job as errored.

    ``api_key`` is forwarded to :func:`extract_diagram_structure` so a
    user-supplied OpenAI key is used instead of the server environment key.
    """
    cb = progress_cb or _noop
    ext = Path(input_path).suffix.lower()

    # --- Stage 1: parse / extract media ------------------------------------
    screenshots = []
    if ext in settings.video_extensions or ext in settings.image_extensions:
        cb("extracting_media", 20, "Extracting media frames")
        out_dir = settings.screenshot_dir / (project_id or "adhoc")
        text_content, screenshots = parse_media(
            input_path,
            output_dir=str(out_dir),
            num_frames=6,
        )
        if not extract_screenshots:
            screenshots = []
    else:
        cb("parsing", 25, "Parsing document")
        if ext == ".docx":
            text_content = parse_docx(input_path)
        elif ext == ".pdf":
            text_content = parse_pdf(input_path)
        else:  # .txt / .md / anything text-like
            with open(input_path, "r", encoding="utf-8", errors="ignore") as fh:
                text_content = fh.read()

    # --- Stage 2: semantic structuring -------------------------------------
    cb("ai_structuring", 60, "Structuring semantic diagram tree")
    structure = extract_diagram_structure(text_content, title=title, api_key=api_key)

    if screenshots:
        for idx, item in enumerate(structure.items):
            if idx < len(screenshots):
                item.screenshot_ref = screenshots[idx]

    # --- Stage 3: layout + compile -----------------------------------------
    cb("compiling", 90, "Compiling Excalidraw visual map")
    excalidraw = build_excalidraw_dict(structure, max_cols=columns)

    problems = validate_excalidraw_dict(excalidraw)
    if problems:
        raise ExcalidrawValidationError("; ".join(problems))

    return excalidraw, len(structure.items)
