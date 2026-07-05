"""
AI Extractor.
Extracts structured DiagramStructure from raw document text using LLM APIs
(via Instructor / OpenAI / Anthropic / Gemini) or intelligent rule-based fallback.
"""
import os
import re
from typing import Optional, List
from ..schemas.diagram_schema import DiagramStructure, DiagramItem

# Matches numbered section headers like "1. Introduction to Make.com" or "3) Flow Control".
_NUMBERED_HEADING = re.compile(r"^\d{1,2}[.)]\s+(?P<title>[A-Z].{1,60})$")


def _is_heading(line: str) -> bool:
    """Heuristic detection of heading-like lines in unstructured text."""
    if line.startswith("#"):
        return True
    # Short ALL-CAPS lines (e.g. "KEY TERMINOLOGY").
    if 3 < len(line) < 60 and line.isupper():
        return True
    # Numbered section headers that read like titles.
    m = _NUMBERED_HEADING.match(line)
    if m:
        title = m.group("title").strip()
        if not title or len(title.split()) > 9 or title.count(",") > 1:
            return False
        # Reject full sentences and table-of-contents lines (which end in a page number).
        if title[-1] in ".!?:;" or title[-1].isdigit():
            return False
        return True
    return False


def _heading_title(line: str) -> str:
    """Extracts a clean title from a heading line."""
    line = re.sub(r"^#+\s*", "", line).strip()
    m = _NUMBERED_HEADING.match(line)
    if m:
        return m.group("title").strip()
    return line.title() if line.isupper() else line

def rule_based_extract(text: str, title: str = "Document Overview") -> DiagramStructure:
    """
    Intelligent rule-based fallback extractor that parses markdown headings,
    paragraphs, and bullet points into a clean DiagramStructure without API calls.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    items = []
    
    current_title = ""
    current_bullets = []
    current_idx = 1
    
    colors = ["purple", "blue", "green", "orange", "yellow", "cyan", "pink"]
    
    for line in lines:
        if _is_heading(line):
            # Save previous item if exists
            if current_title or current_bullets:
                item_id = f"item_{current_idx}"
                items.append(DiagramItem(
                    id=item_id,
                    title=current_title or f"Section {current_idx}",
                    bullet_points=current_bullets[:5] if current_bullets else ["Key concepts discussed in this section."],
                    category_color=colors[(current_idx - 1) % len(colors)],
                    connected_to=[f"item_{current_idx+1}"]
                ))
                current_idx += 1
                current_bullets = []

            current_title = _heading_title(line)
        elif line.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.")):
            clean_pt = re.sub(r"^([-*•]|\d+\.)\s*", "", line).strip()
            if len(clean_pt) > 5:
                current_bullets.append(clean_pt)
        else:
            # Regular sentence, treat as bullet if short enough
            if len(line) > 15 and len(line) < 120 and len(current_bullets) < 4:
                current_bullets.append(line)
                
    # Save last item
    if current_title or current_bullets:
        items.append(DiagramItem(
            id=f"item_{current_idx}",
            title=current_title or f"Section {current_idx}",
            bullet_points=current_bullets[:5] if current_bullets else ["Summary and closing remarks."],
            category_color=colors[(current_idx - 1) % len(colors)],
            connected_to=[]
        ))
        
    # Remove dangling connection on the very last item
    if items and items[-1].connected_to:
        items[-1].connected_to = []
        
    if not items:
        items = [
            DiagramItem(
                id="item_1",
                title="Overview",
                bullet_points=["Key takeaway from document", "Important concept analyzed", "Actionable next steps"],
                category_color="purple",
                connected_to=[]
            )
        ]
        
    return DiagramStructure(
        title=title,
        subtitle="Generated via Doc2Draw Semantic Tree",
        layout_style="multi_column_grid",
        items=items
    )

def extract_diagram_structure(
    text: str,
    title: str = "Document Overview",
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None
) -> DiagramStructure:
    """
    Extracts a semantic DiagramStructure from text using an LLM via Instructor/OpenAI.
    If Instructor/OpenAI is not available or API key is not set, falls back to rule_based_extract.
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return rule_based_extract(text, title)
        
    try:
        import instructor
        from openai import OpenAI
        
        client = instructor.from_openai(OpenAI(api_key=api_key))
        
        prompt = f"""
You are an expert curriculum architect and visual designer.
Analyze the following document text and break it down into a structured diagram map.
Extract 3 to 12 core concepts/chapters as DiagramItem cards.
For each card:
- Give a clear, engaging title.
- Provide 3 to 5 concise bullet points of key takeaways.
- Assign a harmonious category_color ('purple', 'blue', 'green', 'orange', 'red', 'cyan', 'pink').
- Connect sequential or related cards via 'connected_to' IDs (e.g., item_1 connects to item_2).

Document Title: {title}
Document Content:
{text[:12000]}
"""
        structure = client.chat.completions.create(
            model=model,
            response_model=DiagramStructure,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return structure
    except Exception as e:
        # Fallback to rule-based extraction if LLM fails
        return rule_based_extract(text, title)
