"""
API v1 Router - aggregates all route modules.
"""
from fastapi import APIRouter

from app.api.v1.routes import health, agents, documents, chat, workflows

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])