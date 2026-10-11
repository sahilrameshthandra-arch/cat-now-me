"""
Health check endpoints.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import structlog

from app.services.ollama_service import ollama_service
from app.services.vector_store import vector_store_service
from app.core.database import engine
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class DetailedHealthResponse(HealthResponse):
    ollama: dict
    database: dict
    vector_store: dict


@router.get("", response_model=HealthResponse)
async def health_check():
    """Basic health check."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Detailed health check with dependency status."""
    # Check Ollama
    ollama_healthy = await ollama_service.health_check()
    ollama_models = []
    if ollama_healthy:
        try:
            models = await ollama_service.list_models()
            ollama_models = [m.name for m in models]
        except Exception:
            pass
    
    # Check Database
    db_healthy = False
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_healthy = True
    except Exception:
        pass
    
    # Check Vector Store
    vs_healthy = False
    vs_count = 0
    try:
        stats = await vector_store_service.get_collection_stats()
        vs_healthy = True
        vs_count = stats.get("document_count", 0)
    except Exception:
        pass
    
    return DetailedHealthResponse(
        status="healthy" if all([ollama_healthy, db_healthy, vs_healthy]) else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        ollama={
            "status": "healthy" if ollama_healthy else "unhealthy",
            "base_url": settings.OLLAMA_BASE_URL,
            "models": ollama_models,
        },
        database={
            "status": "healthy" if db_healthy else "unhealthy",
            "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "configured",
        },
        vector_store={
            "status": "healthy" if vs_healthy else "unhealthy",
            "collection": settings.CHROMA_COLLECTION,
            "document_count": vs_count,
        },
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    ollama_healthy = await ollama_service.health_check()
    
    db_healthy = False
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_healthy = True
    except Exception:
        pass
    
    if not (ollama_healthy and db_healthy):
        return {"status": "not ready"}, 503
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}