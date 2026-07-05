"""Small shared helpers."""
import uuid


def new_id(prefix: str) -> str:
    """Generate a short, prefixed unique id (e.g. 'proj_ab12cd34ef56')."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
