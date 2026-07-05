"""
Media Parser.
Extracts keyframe screenshots from video files using OpenCV.
"""
import os
from typing import List, Tuple

def extract_video_screenshots(video_path: str, output_dir: str = ".", num_frames: int = 9, prefix: str = "screenshot") -> List[str]:
    """
    Extracts evenly distributed screenshots from a video file.
    Returns a list of saved screenshot filepaths.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    try:
        import cv2
    except ImportError:
        raise ImportError("Please install 'opencv-python' to extract video screenshots: pip install opencv-python")
        
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {video_path}")
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return []
        
    saved_files = []
    # Generate evenly distributed percentages across the video duration (avoiding absolute 0% and 100%)
    step = 1.0 / (num_frames + 1)
    percentages = [step * i for i in range(1, num_frames + 1)]
    
    for idx, p in enumerate(percentages):
        frame_no = int(total_frames * p)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = cap.read()
        if ret:
            filename = os.path.join(output_dir, f"{prefix}_{idx+1}.jpg")
            cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            saved_files.append(filename)
            
    cap.release()
    return saved_files


def parse_media(
    media_path: str,
    output_dir: str = ".",
    num_frames: int = 6,
) -> Tuple[str, List[str]]:
    """
    Guide-aligned entrypoint used by the backend worker.

    Handles both videos (extracts evenly spaced keyframes) and single images
    (treats the file itself as the only frame). Returns a tuple of
    ``(raw_text, image_paths)`` where ``raw_text`` is a markdown scaffold the
    AI extractor can turn into a diagram and ``image_paths`` are the frames to
    embed onto the cards.
    """
    if not os.path.exists(media_path):
        raise FileNotFoundError(f"Media file not found: {media_path}")

    ext = os.path.splitext(media_path)[1].lower()
    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    if ext in image_exts:
        images = [media_path]
    else:
        images = extract_video_screenshots(
            media_path, output_dir=output_dir, num_frames=num_frames
        )

    title = os.path.splitext(os.path.basename(media_path))[0].replace("_", " ").title()
    section_count = max(len(images), 1)
    raw_text = f"# {title}\n\nVisual walkthrough across {section_count} key sections."
    for i in range(section_count):
        raw_text += (
            f"\n\n## Section {i + 1}\n"
            "- Visual demonstration of a core topic\n"
            "- Step-by-step walkthrough\n"
            "- Practical tips and techniques"
        )

    return raw_text, images
