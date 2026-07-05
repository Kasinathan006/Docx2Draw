"""
Excalidraw Element Primitives & Styling Palettes.
"""
import base64
import os
from datetime import datetime


def now_ms() -> int:
    """Current epoch time in milliseconds (Excalidraw timestamp format)."""
    return int(datetime.now().timestamp() * 1000)

COLOR_PALETTES = {
    "purple": {"bg": "#f3e8ff", "stroke": "#7e22ce", "text": "#3b0764"},
    "blue": {"bg": "#eff6ff", "stroke": "#2563eb", "text": "#1e3a8a"},
    "green": {"bg": "#f0fdf4", "stroke": "#16a34a", "text": "#14532d"},
    "orange": {"bg": "#fff7ed", "stroke": "#ea580c", "text": "#7c2d12"},
    "yellow": {"bg": "#fef3c7", "stroke": "#d97706", "text": "#78350f"},
    "red": {"bg": "#fef2f2", "stroke": "#dc2626", "text": "#7f1d1d"},
    "slate": {"bg": "#f8fafc", "stroke": "#475569", "text": "#0f172a"},
    "pink": {"bg": "#fdf2f8", "stroke": "#db2777", "text": "#831843"},
    "cyan": {"bg": "#ecfeff", "stroke": "#0891b2", "text": "#164e63"},
}

def get_image_base64_and_dimensions(filepath: str) -> str:
    """Reads an image file and returns a data URL (base64)."""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        data = f.read()
    b64_str = base64.b64encode(data).decode("utf-8")
    ext = os.path.splitext(filepath)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64_str}"

def create_element(
    id: str,
    type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    bg_color: str = "#ffffff",
    stroke_color: str = "#000000",
    text: str = "",
    font_size: int = 16,
    stroke_width: int = 2,
    text_align: str = "left",
    roundness: int = 8
) -> dict:
    """Creates a standard Excalidraw element (rectangle, ellipse, text, etc.)."""
    elem = {
        "id": id,
        "type": type,
        "x": float(x),
        "y": float(y),
        "width": float(width),
        "height": float(height),
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": bg_color,
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 3} if roundness else None,
        "seed": abs(hash(id)) % 100000,
        "version": 1,
        "versionNonce": abs(hash(id)) % 100000,
        "isDeleted": False,
        "boundElements": [],
        "updatedAt": int(datetime.now().timestamp() * 1000),
        "link": None,
        "locked": False
    }
    if type == "text":
        elem.update({
            "text": text,
            "fontSize": font_size,
            "fontFamily": 1,
            "textAlign": text_align,
            "verticalAlign": "top",
            "baseline": int(font_size * 0.8),
            "lineHeight": 1.25,
            "backgroundColor": "transparent"
        })
    elif type == "rectangle" and text:
        text_id = f"{id}_text"
        elem["boundElements"].append({"id": text_id, "type": "text"})
    return elem

def create_bound_text(
    parent_id: str,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    font_size: int = 15,
    stroke_color: str = "#1e293b",
    text_align: str = "left"
) -> dict:
    """Creates a text element bound inside a parent container."""
    return {
        "id": f"{parent_id}_text",
        "type": "text",
        "x": float(x + 15),
        "y": float(y + 15),
        "width": float(width - 30),
        "height": float(height - 30),
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": abs(hash(parent_id)) % 100000,
        "version": 1,
        "versionNonce": abs(hash(parent_id)) % 100000,
        "isDeleted": False,
        "boundElements": [],
        "updatedAt": int(datetime.now().timestamp() * 1000),
        "link": None,
        "locked": False,
        "text": text,
        "fontSize": font_size,
        "fontFamily": 1,
        "textAlign": text_align,
        "verticalAlign": "top",
        "baseline": int(font_size * 0.8),
        "lineHeight": 1.3,
        "containerId": parent_id
    }

def create_arrow(
    id: str,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    stroke_color: str = "#64748b"
) -> dict:
    """Creates a curved arrow connecting two coordinates."""
    return {
        "id": id,
        "type": "arrow",
        "x": float(start_x),
        "y": float(start_y),
        "width": float(abs(end_x - start_x)),
        "height": float(abs(end_y - start_y)),
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": abs(hash(id)) % 100000,
        "version": 1,
        "versionNonce": abs(hash(id)) % 100000,
        "isDeleted": False,
        "boundElements": [],
        "updatedAt": int(datetime.now().timestamp() * 1000),
        "link": None,
        "locked": False,
        "points": [[0, 0], [float(end_x - start_x), float(end_y - start_y)]],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": "arrow"
    }

def create_image_element(
    id: str,
    file_id: str,
    x: float,
    y: float,
    width: float,
    height: float
) -> dict:
    """Creates an image element referencing an embedded file_id."""
    return {
        "id": id,
        "type": "image",
        "x": float(x),
        "y": float(y),
        "width": float(width),
        "height": float(height),
        "angle": 0,
        "strokeColor": "transparent",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": abs(hash(id)) % 100000,
        "version": 1,
        "versionNonce": abs(hash(id)) % 100000,
        "isDeleted": False,
        "boundElements": [],
        "updatedAt": int(datetime.now().timestamp() * 1000),
        "status": "saved",
        "fileId": file_id,
        "scale": [1, 1],
        "link": None,
        "locked": False
    }
