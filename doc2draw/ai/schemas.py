"""
AI schemas (guide-aligned import path).

The canonical Pydantic models live in :mod:`doc2draw.schemas.diagram_schema`.
This module re-exports them at the ``doc2draw.ai.schemas`` path used by the
Full-Stack Implementation Guide so both import styles work interchangeably.
"""
from ..schemas.diagram_schema import DiagramItem, DiagramStructure

__all__ = ["DiagramItem", "DiagramStructure"]
