"""
Parsers module for reading .docx, .pdf, and extracting video screenshots.
"""
from .docx_parser import parse_docx
from .pdf_parser import parse_pdf
from .media_parser import extract_video_screenshots, parse_media

__all__ = ["parse_docx", "parse_pdf", "extract_video_screenshots", "parse_media"]
