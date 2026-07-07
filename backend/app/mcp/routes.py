"""Rotas MCP via SSE — sub-app ASGI montavel no FastAPI.

Disponibiliza o protocolo MCP sobre HTTP atraves de:

  GET  /api/v1/mcp/sse      — conexao SSE (EventSource)
  POST /api/v1/mcp/message  — envio de mensagens JSON-RPC

Uso em main.py:
    from app.mcp.routes import mcp_sse_app
    app.mount("/api/v1/mcp", app=mcp_sse_app)
"""

import logging

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from app.mcp.server import MCPServerProvider
from app.mcp.transport import MCPSseTransport

logger = logging.getLogger(__name__)

# Instancia unica do transporte SSE (singleton no modulo)
_transport = MCPSseTransport(message_endpoint="/api/v1/mcp/message")


# ── Handlers ASGI ───────────────────────────────────────────────────


async def _handle_sse(request: Request) -> None:
    """GET /sse — estabelece conexao SSE com o cliente MCP."""
    logger.info("Requisição SSE MCP recebida")
    await _transport.handle_sse(request)


async def _handle_message(request: Request) -> None:
    """POST /message — recebe mensagens JSON-RPC do cliente."""
    logger.debug("Requisição POST /message recebida")
    await _transport.handle_message(request)


# ── Sub-app Starlette ───────────────────────────────────────────────

mcp_sse_app = Starlette(
    routes=[
        Route("/sse", endpoint=_handle_sse, methods=["GET"]),
        Mount(
            "/message",
            app=_transport._sse.handle_post_message,
        ),
    ],
    on_startup=[],
    on_shutdown=[],
)
