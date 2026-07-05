"""
Doc2Draw CLI.
Command-line interface for generating Excalidraw maps from documents or videos.
"""
import os
import sys
import argparse
from .utils import safe_print
from .parsers.docx_parser import parse_docx
from .parsers.pdf_parser import parse_pdf
from .parsers.media_parser import extract_video_screenshots
from .ai.extractor import extract_diagram_structure
from .compiler.excalidraw_compiler import save_excalidraw_file

def main():
    parser = argparse.ArgumentParser(
        description="✨ Doc2Draw: Turn Documents & Videos into Interactive Excalidraw Visual Maps ✨"
    )
    parser.add_argument("input", help="Path to input file (.docx, .pdf, .txt, .mp4, etc.)")
    parser.add_argument("-o", "--output", help="Path for output .excalidraw file", default=None)
    parser.add_argument("-t", "--title", help="Title for the visual map", default=None)
    parser.add_argument("--cols", type=int, help="Number of columns in grid layout", default=3)
    parser.add_argument("--screenshots", action="store_true", help="Extract video screenshots and attach to cards")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        safe_print(f"❌ Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
        
    ext = os.path.splitext(args.input)[1].lower()
    title = args.title or os.path.splitext(os.path.basename(args.input))[0].replace("_", " ").title()
    output_path = args.output or f"{os.path.splitext(args.input)[0]}.excalidraw"
    
    safe_print(f"📄 Processing '{args.input}'...")
    
    text_content = ""
    screenshots = []
    
    if ext == ".docx":
        text_content = parse_docx(args.input)
    elif ext == ".pdf":
        text_content = parse_pdf(args.input)
    elif ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        safe_print("🎥 Video detected! Extracting screenshots...")
        output_dir = os.path.join(os.path.dirname(output_path), "_screenshots")
        screenshots = extract_video_screenshots(args.input, output_dir=output_dir, num_frames=6)
        text_content = f"# {title}\n\nVideo masterclass covering key concepts and visual demonstrations across {len(screenshots)} sections."
        for idx in range(len(screenshots)):
            text_content += f"\n\n## Section {idx+1}\n- Visual demonstration of core topic {idx+1}\n- Step-by-step walkthrough in video\n- Practical tips and techniques"
    else:
        # Default text file
        with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
            text_content = f.read()
            
    safe_print("🤖 Extracting semantic diagram structure...")
    structure = extract_diagram_structure(text_content, title=title)
    
    # Attach screenshots if extracted
    if screenshots:
        for idx, item in enumerate(structure.items):
            if idx < len(screenshots):
                item.screenshot_ref = screenshots[idx]
                
    safe_print(f"🎨 Compiling Excalidraw visual map ({len(structure.items)} chapters)...")
    save_excalidraw_file(structure, output_path, max_cols=args.cols)
    
    safe_print(f"✅ Successfully created visual map: {output_path}")

if __name__ == "__main__":
    main()
