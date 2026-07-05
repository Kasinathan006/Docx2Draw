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
    Handles long text documents by chunking into sequential cards.
    """
    # Split text into paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
    items = []
    current_title = ""
    current_bullets = []
    current_idx = 1
    
    colors = ["purple", "blue", "green", "orange", "yellow", "cyan", "pink"]
    
    def save_item():
        nonlocal current_title, current_bullets, current_idx
        if current_title or current_bullets:
            items.append(DiagramItem(
                id=f"item_{current_idx}",
                title=current_title or f"Section {current_idx}",
                bullet_points=current_bullets[:5] if current_bullets else ["Key concepts discussed in this section."],
                category_color=colors[(current_idx - 1) % len(colors)],
                connected_to=[]
            ))
            current_idx += 1
            current_title = ""
            current_bullets = []

    for para in paragraphs:
        lines = [line.strip() for line in para.split('\n') if line.strip()]
        if not lines:
            continue
            
        first_line = lines[0]
        if _is_heading(first_line):
            save_item()
            current_title = _heading_title(first_line)
            process_lines = lines[1:]
        else:
            process_lines = lines
            
        for line in process_lines:
            if line.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.")):
                clean_pt = re.sub(r"^([-*•]|\d+\.)\s*", "", line).strip()
                if len(clean_pt) > 5:
                    current_bullets.append(clean_pt[:150])
            else:
                # Regular sentence, break long lines into sentences
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', line) if s.strip()]
                for s in sentences:
                    if len(s) > 10:
                        current_bullets.append(s[:150])
                        
            # If item gets too large, start a new one
            if len(current_bullets) >= 5:
                save_item()
                
    # Save any remaining data
    save_item()
    
    # Post-process to limit total items and connect them sequentially
    if len(items) > 12:
        items = items[:12]
        
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
        
    # Connect sequential items
    for i in range(len(items) - 1):
        items[i].connected_to = [items[i+1].id]
        
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
