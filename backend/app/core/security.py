"""
Security & CORS configuration (guide §5.1 core/security.py).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
