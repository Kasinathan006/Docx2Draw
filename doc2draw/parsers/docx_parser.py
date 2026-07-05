"""
DOCX Parser.
Extracts clean structured text and headings from .docx documents.
"""
import os
import zipfile
import xml.etree.ElementTree as ET

def parse_docx(filepath: str) -> str:
    """
    Parses a .docx file and returns clean text.
    Uses zipfile XML extraction for speed and zero-dependency resilience,
    or falls back/enhances with python-docx if installed.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    try:
        import docx
        doc = docx.Document(filepath)
        text_lines = []
        for p in doc.paragraphs:
            if not p.text.strip():
                continue
            # Style (and its name) may be None for paragraphs with no explicit style.
            style_name = getattr(getattr(p, "style", None), "name", None) or ""
            if style_name.startswith("Heading"):
                level = style_name.replace("Heading", "").strip()
                prefix = "#" * int(level) if level.isdigit() else "#"
                text_lines.append(f"\n{prefix} {p.text.strip()}")
            else:
                text_lines.append(p.text.strip())
        return "\n".join(text_lines)
    except ImportError:
        # Fast fallback using zipfile XML parsing
        with zipfile.ZipFile(filepath) as zf:
            xml_content = zf.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        
        paragraphs = []
        for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
            if texts:
                paragraphs.append(''.join(texts))
        return "\n".join(paragraphs)
