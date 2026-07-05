"""
PDF Parser.
Extracts clean text from PDF files using pypdf or pdfplumber.
"""
import os

def parse_pdf(filepath: str) -> str:
    """Parses a .pdf file and returns clean text."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    try:
        import pdfplumber
        text_lines = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_lines.append(text)
        return "\n\n--- PAGE BREAK ---\n\n".join(text_lines)
    except ImportError:
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            text_lines = [page.extract_text() for page in reader.pages if page.extract_text()]
            return "\n\n--- PAGE BREAK ---\n\n".join(text_lines)
        except ImportError:
            raise ImportError("Please install 'pdfplumber' or 'pypdf' to parse PDF files: pip install pdfplumber pypdf")
