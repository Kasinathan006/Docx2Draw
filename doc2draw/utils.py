"""
Shared utilities for Doc2Draw.
Provides cross-platform-safe console output (Windows consoles often use a
legacy code page like cp1252 that cannot encode emoji, which crashes print()).
"""
import sys


def _reconfigure_stdio() -> None:
    """Force UTF-8 on stdout/stderr when the stream supports reconfiguration."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                # Stream may be detached or non-reconfigurable (e.g. captured pipes)
                pass


# Attempt UTF-8 reconfiguration once at import time.
_reconfigure_stdio()


def safe_print(*args, **kwargs) -> None:
    """
    print() that never raises UnicodeEncodeError.

    Falls back to an ASCII-safe rendering of the message if the active console
    encoding cannot represent every character (typically emoji on Windows).
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        safe_args = [
            str(a).encode(encoding, errors="replace").decode(encoding)
            for a in args
        ]
        print(*safe_args, **kwargs)
