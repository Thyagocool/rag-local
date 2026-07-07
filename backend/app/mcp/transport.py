"""Transporte SSE para o servidor MCP.

Permite que clientes MCP se conectem via HTTP/SSE em vez de stdio,
usando o protocolo Server-Sent Events (SSE) do pacote mcp.

Uso:
    transport = MCPSseTransport(message_endpoint="/api/v1/mcp/message")
    await transport.handle_sse(request)       # GET  → SSE stream
    await transport.handle_message(request)   # POST → JSON-RPC
"""

import logging

from mcp.server.sse import SseServerTransport
from starlette.requests import Request

from app.mcp.server import MCPServerProvider

logger = logging.getLogger(__name__)


class MCPSseTransport:
    """Adaptador SSE para o servidor MCP.

    Converte o transporte SSE (HTTP/EventStream) para o protocolo MCP,
    permitindo que clientes MCP (Claude Desktop, Cline, etc.) se
    conectem via HTTP em vez de stdio.

    Attributes:
        message_endpoint: URL relativa onde o cliente deve enviar as
            mensagens JSON-RPC de resposta (ex: "/api/v1/mcp/message").
    """

    def __init__(self, message_endpoint: str = "/api/v1/mcp/message"):
        self._sse = SseServerTransport(message_endpoint)
        logger.debug(
            "MCPSseTransport inicializado com endpoint: %s",
            message_endpoint,
        )

    # ── Handlers publicos ───────────────────────────────────────────

    async def handle_sse(self, request: Request) -> None:
        """Estabelece conexao SSE com o cliente MCP.

        Este metodo deve ser chamado a partir de um handler HTTP GET.
        Ele mantem a conexao aberta enquanto o cliente estiver
        conectado, enviando eventos SSE.

        Args:
            request: Request do Starlette/FastAPI.
        """
        server = MCPServerProvider.get_server()
        options = MCPServerProvider.get_init_options()

        logger.info("Nova conexao SSE MCP estabelecida")
        async with self._sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as streams:
            read_stream, write_stream = streams
            await server.run(read_stream, write_stream, options)
        logger.info("Conexao SSE MCP encerrada")

    async def handle_message(self, request: Request) -> None:
        """Recebe mensagens JSON-RPC do cliente MCP via POST.

        O cliente deve enviar o session_id (retornado no evento
        'endpoint' do SSE) como query parameter.

        Args:
            request: Request do Starlette/FastAPI.
        """
        logger.debug("Mensagem JSON-RPC recebida via POST")
        await self._sse.handle_post_message(
            request.scope,
            request.receive,
            request._send,
        )
