"""Agregador de rotas — inclui todos os modulos de rota."""

from fastapi import APIRouter

from app.api.rag_routes import router as rag_router
from app.api.agent_routes import router as agent_router
from app.api.health_routes import router as health_router

router = APIRouter()
router.include_router(rag_router)
router.include_router(agent_router)
router.include_router(health_router)
