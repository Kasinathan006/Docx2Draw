"""Main API v1 router — aggregates all endpoint routers (guide §5.1)."""
from fastapi import APIRouter

from .endpoints import projects, users, webhooks

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects.router)
api_router.include_router(users.router)
api_router.include_router(webhooks.router)
