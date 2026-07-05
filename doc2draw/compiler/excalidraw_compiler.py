"""
Excalidraw Compiler.
Converts a DiagramStructure into a valid Excalidraw JSON string or file.
"""
import json
from typing import Dict, Any, List
from ..schemas.diagram_schema import DiagramStructure
from ..layout.grid_engine import GridEngine

# Minimum attributes every Excalidraw element must carry to load without errors.
_REQUIRED_ELEMENT_ATTRS = (
    "id", "type", "x", "y", "width", "height",
    "strokeColor", "backgroundColor", "seed", "version",
)


class ExcalidrawValidationError(ValueError):
    """Raised when a compiled diagram does not satisfy the Excalidraw schema."""


def build_excalidraw_dict(structure: DiagramStructure, max_cols: int = 3) -> Dict[str, Any]:
    """Builds the Excalidraw document as a plain dict (elements + files + appState)."""
    engine = GridEngine(max_cols=max_cols)
    elements, files = engine.generate_layout(structure)

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://doc2draw.ai",
        "elements": elements,
        "appState": {
            "gridSize": 20,
            "viewBackgroundColor": "#ffffff",
        },
        "files": files,
    }


def validate_excalidraw_dict(data: Dict[str, Any]) -> List[str]:
    """
    Validates an Excalidraw document dict against the core schema requirements.
    Returns a list of human-readable problems (empty list == valid).
    """
    problems: List[str] = []

    if data.get("type") != "excalidraw":
        problems.append("Top-level 'type' must be 'excalidraw'.")
    if not isinstance(data.get("version"), int):
        problems.append("Top-level 'version' must be an integer.")
    for key in ("elements", "appState", "files"):
        if key not in data:
            problems.append(f"Missing top-level key '{key}'.")

    elements = data.get("elements", [])
    if not isinstance(elements, list):
        problems.append("'elements' must be a list.")
        return problems

    seen_ids = set()
    file_ids = set(data.get("files", {}).keys())

    for i, el in enumerate(elements):
        eid = el.get("id", f"<index {i}>")
        for attr in _REQUIRED_ELEMENT_ATTRS:
            if attr not in el:
                problems.append(f"Element '{eid}' missing required attribute '{attr}'.")
        if el.get("id") in seen_ids:
            problems.append(f"Duplicate element id '{eid}'.")
        seen_ids.add(el.get("id"))

        # Bound text must point at an existing container, and vice-versa.
        if el.get("type") == "text" and el.get("containerId") is not None:
            if el["containerId"] not in seen_ids and el["containerId"] not in {e.get("id") for e in elements}:
                problems.append(f"Text '{eid}' references missing container '{el['containerId']}'.")

        # Image elements must reference an embedded file.
        if el.get("type") == "image":
            fid = el.get("fileId")
            if fid not in file_ids:
                problems.append(f"Image '{eid}' references missing fileId '{fid}'.")

    return problems


def compile_to_excalidraw_json(structure: DiagramStructure, max_cols: int = 3, validate: bool = True) -> str:
    """Compiles a DiagramStructure into a formatted Excalidraw JSON string."""
    excalidraw_data = build_excalidraw_dict(structure, max_cols=max_cols)

    if validate:
        problems = validate_excalidraw_dict(excalidraw_data)
        if problems:
            raise ExcalidrawValidationError(
                "Compiled Excalidraw document failed validation:\n  - "
                + "\n  - ".join(problems)
            )

    return json.dumps(excalidraw_data, indent=2)


def save_excalidraw_file(structure: DiagramStructure, output_path: str, max_cols: int = 3, validate: bool = True) -> str:
    """Compiles and writes an Excalidraw JSON file to disk."""
    json_str = compile_to_excalidraw_json(structure, max_cols=max_cols, validate=validate)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_str)
    return output_path
