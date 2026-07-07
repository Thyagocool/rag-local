"""Modulo MCP — servidor e transportes do Model Context Protocol.

Fornece ferramentas do RAG via protocolo MCP usando:
  - stdio: para Claude Desktop, Cline e outros clientes CLI
  - SSE:  para conexoes HTTP em tempo real (EventSource)

Exported components:
    MCPServerProvider  — provider singleton do servidor MCP
    MCPSseTransport   — adaptador de transporte SSE
    mcp_sse_app       — sub-app ASGI Starlette para montagem no FastAPI
"""

from app.mcp.server import MCPServerProvider
from app.mcp.transport import MCPSseTransport
from app.mcp.routes import mcp_sse_app

__all__ = [
    "MCPServerProvider",
    "MCPSseTransport",
    "mcp_sse_app",
]
