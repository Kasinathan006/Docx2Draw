"""
Deterministic Grid Engine for Excalidraw Layouts.
Calculates X, Y positions, container heights, and arrow routing.
"""
from typing import List, Dict, Any, Tuple
from ..schemas.diagram_schema import DiagramStructure, DiagramItem
from .excalidraw_elements import (
    create_element,
    create_bound_text,
    create_arrow,
    create_image_element,
    get_image_base64_and_dimensions,
    now_ms as _now_ms,
    COLOR_PALETTES
)

class GridEngine:
    def __init__(
        self,
        col_width: float = 750.0,
        col_gap: float = 120.0,
        row_gap: float = 60.0,
        start_x: float = 0.0,
        start_y: float = 0.0,
        max_cols: int = 3
    ):
        self.col_width = col_width
        self.col_gap = col_gap
        self.row_gap = row_gap
        self.start_x = start_x
        self.start_y = start_y
        self.max_cols = max_cols

    def calculate_card_height(self, item: DiagramItem) -> float:
        """Dynamically calculates card height based on bullet points and title length."""
        base_height = 120.0
        line_height = 28.0
        for pt in item.bullet_points:
            # Estimate wrap lines (approx 70 chars per line for 750px width)
            lines = max(1, len(pt) // 70 + 1)
            base_height += lines * line_height
        if item.screenshot_ref:
            base_height += 360.0 # Space for image preview
        return max(base_height, 220.0)

    def generate_layout(self, structure: DiagramStructure) -> Tuple[List[dict], Dict[str, str]]:
        """
        Takes a semantic DiagramStructure and compiles it into Excalidraw elements and embedded files.
        Returns (elements_list, files_dict).
        """
        elements = []
        files = {}
        
        # 1. Header Banner
        banner_width = self.max_cols * self.col_width + (self.max_cols - 1) * self.col_gap
        banner_height = 160.0
        header_text = f"✨ {structure.title.upper()} ✨\n"
        header_text += "=" * min(80, len(structure.title) * 2) + "\n"
        if structure.subtitle:
            header_text += f"{structure.subtitle}\n"
            
        header_rect = create_element("header_banner", "rectangle", self.start_x, self.start_y, banner_width, banner_height, "#f3e8ff", "#7e22ce")
        header_rect["boundElements"] = [{"id": "header_banner_text", "type": "text"}]
        elements.append(header_rect)
        elements.append(create_bound_text("header_banner", header_text, self.start_x, self.start_y, banner_width, banner_height, 20, "#3b0764", "center"))

        # 2. Arrange Cards in Grid
        col_y_offsets = [self.start_y + banner_height + self.row_gap] * self.max_cols
        card_positions = {} # id -> (center_x, center_y, width, height)
        
        for idx, item in enumerate(structure.items):
            col_idx = idx % self.max_cols
            x = self.start_x + col_idx * (self.col_width + self.col_gap)
            y = col_y_offsets[col_idx]
            
            height = self.calculate_card_height(item)
            palette = COLOR_PALETTES.get(item.category_color, COLOR_PALETTES["slate"])
            
            # Create Card Container (bound to its text, and to its image if present)
            card_rect = create_element(item.id, "rectangle", x, y, self.col_width, height, palette["bg"], palette["stroke"])
            card_rect["boundElements"] = [{"id": f"{item.id}_text", "type": "text"}]

            # Format Card Text
            card_text = f"{idx+1}. {item.title}\n"
            card_text += "-" * min(60, len(item.title) * 2) + "\n"
            for pt in item.bullet_points:
                card_text += f"• {pt}\n"

            text_height = height - (360.0 if item.screenshot_ref else 0.0)

            # Embed Screenshot if present
            if item.screenshot_ref:
                file_id = f"file_{item.id}"
                data_url = get_image_base64_and_dimensions(item.screenshot_ref)
                if data_url:
                    files[file_id] = {
                        "id": file_id,
                        "dataURL": data_url,
                        "mimeType": "image/jpeg" if data_url.startswith("data:image/jpeg") else "image/png",
                        "created": _now_ms(),
                    }
                    img_w = self.col_width - 60.0
                    img_h = 320.0
                    img_x = x + 30.0
                    img_y = y + text_height - 10.0
                    img_id = f"img_{item.id}"
                    elements.append(create_image_element(img_id, file_id, img_x, img_y, img_w, img_h))

            elements.append(card_rect)
            elements.append(create_bound_text(item.id, card_text, x, y, self.col_width, text_height, 16, palette["text"]))
            
            # Save position for arrow routing
            card_positions[item.id] = (x, y, self.col_width, height)
            col_y_offsets[col_idx] = y + height + self.row_gap

        # 3. Generate Connecting Arrows
        for item in structure.items:
            if not item.connected_to or item.id not in card_positions:
                continue
            start_x, start_y, start_w, start_h = card_positions[item.id]
            for target_id in item.connected_to:
                if target_id in card_positions:
                    end_x, end_y, end_w, end_h = card_positions[target_id]
                    
                    # Connect right center of start card to left center of end card (if left-to-right)
                    # Or bottom center to top center (if top-to-bottom in same col)
                    if start_x < end_x:
                        arrow_start = (start_x + start_w, start_y + start_h / 2.0)
                        arrow_end = (end_x, end_y + end_h / 2.0)
                    elif start_x > end_x:
                        arrow_start = (start_x, start_y + start_h / 2.0)
                        arrow_end = (end_x + end_w, end_y + end_h / 2.0)
                    else:
                        arrow_start = (start_x + start_w / 2.0, start_y + start_h)
                        arrow_end = (end_x + end_w / 2.0, end_y)
                        
                    arrow_id = f"arrow_{item.id}_{target_id}"
                    palette = COLOR_PALETTES.get(item.category_color, COLOR_PALETTES["slate"])
                    elements.append(create_arrow(arrow_id, arrow_start[0], arrow_start[1], arrow_end[0], arrow_end[1], palette["stroke"]))

        return elements, files
