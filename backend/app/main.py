"""FastAPI App — RAG + Agentes + MCP."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
from app.mcp.routes import mcp_sse_app
from app.infra.tracing import tracing_manager

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.app_version)

# ── Tracing (OpenTelemetry) ───────────────────────────────────────────
if settings.tracing_enabled:
    try:
        tracing_manager.setup(
            service_name=settings.app_name,
            otlp_endpoint=settings.tracing_otlp_endpoint,
        )
        tracing_manager.instrument_app(app)
        tracing_manager.instrument_httpx()
        logger.info("OpenTelemetry tracing ativado")
    except Exception as exc:
        logger.warning("Falha ao inicializar tracing: %s", exc)

# ── CORS — libera geral pra desenvolvimento ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rotas REST ────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")

# ── MCP via SSE (sub-app ASGI montado em /api/v1/mcp) ─────────────────
app.mount("/api/v1/mcp", app=mcp_sse_app)

# ── Shutdown hook ─────────────────────────────────────────────────────
@app.on_event("shutdown")
def shutdown_tracing():
    if settings.tracing_enabled:
        tracing_manager.shutdown()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
