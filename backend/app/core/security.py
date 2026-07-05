"""
Security & CORS configuration.

Supports both explicit origins and wildcard (*). If CORS_ORIGINS contains
only "*", allow_origin_regex is also set to permit all Vercel preview URLs.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings


def configure_cors(app: FastAPI) -> None:
    origins = settings.cors_origin_list
    # If the operator configured "*" treat it as truly open (dev / Render preview)
    if "*" in origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,   # credentials not allowed with wildcard origins
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # Always include localhost variants + allow any Vercel preview domain
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_origin_regex=r"https://.*\.vercel\.app",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
