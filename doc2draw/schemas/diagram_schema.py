"""
Pydantic Schemas for Doc2Draw Semantic Diagram Tree.
"""
from typing import List, Optional, Dict, Any
try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback lightweight implementation if pydantic is not installed
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            return self.__dict__
        def dict(self):
            return self.__dict__
    def Field(default=None, **kwargs):
        return default

class DiagramItem(BaseModel):
    """
    Represents a single card/node/chapter in the Excalidraw visual map.
    """
    id: str = Field(..., description="Unique identifier, e.g., 'item_1'")
    title: str = Field(..., description="Short title or heading of the card")
    bullet_points: List[str] = Field(..., description="3 to 5 key takeaway points")
    category_color: str = Field(default="purple", description="Color theme: 'blue', 'green', 'purple', 'orange', 'red', 'slate'")
    connected_to: Optional[List[str]] = Field(default_factory=list, description="IDs of items this should connect to via arrows")
    screenshot_ref: Optional[str] = Field(default=None, description="Path or filename of associated screenshot if applicable")

class DiagramStructure(BaseModel):
    """
    Represents the complete semantic diagram tree for a document or masterclass.
    """
    title: str = Field(..., description="Main title of the entire masterclass/document")
    subtitle: str = Field(default="", description="One-line summary subtitle")
    layout_style: str = Field(default="multi_column_grid", description="Layout type: 'multi_column_grid', 'flowchart_pipeline', 'mindmap_tree'")
    items: List[DiagramItem] = Field(default_factory=list, description="List of diagram items/chapters")
