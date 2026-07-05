"""Rota de health check do servico."""

from fastapi import APIRouter
from app.api.schemas import HealthResponse
from app.rag.vectorstore import list_collections
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check do servico."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        vector_collections=list_collections(),
    )
