"""Provedor do servidor MCP e definicao das ferramentas.

Separa a criacao do servidor MCP (SRP) do transporte usado
(stdio, SSE, etc.). Qualquer transporte pode chamar MCPServerProvider
para obter a instância do servidor e as opcoes de inicializacao.
"""

import asyncio
import logging
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from app.rag.use_cases.ask_use_case import AskUseCase

logger = logging.getLogger(__name__)


class MCPServerProvider:
    """Provider singleton do servidor MCP e suas ferramentas.

    Cria o Server uma unica vez (cacheado) e oferece metodos de
    classe para obter a instancia e as opcoes de inicializacao.

    Uso:
        server = MCPServerProvider.get_server()
        options = MCPServerProvider.get_init_options()
        await server.run(read_stream, write_stream, options)
    """

    _instance: Server | None = None

    # ── API publica ─────────────────────────────────────────────────

    @classmethod
    def get_server(cls) -> Server:
        """Retorna a instancia unica do servidor MCP (singleton)."""
        if cls._instance is None:
            cls._instance = cls._build_server()
        return cls._instance

    @classmethod
    def get_init_options(cls) -> InitializationOptions:
        """Retorna as opcoes de inicializacao padrao."""
        server = cls.get_server()
        return InitializationOptions(
            server_name="rag-mcp-server",
            server_version="0.1.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )

    @classmethod
    def reset(cls):
        """Limpa o cache — util em testes ou reload."""
        cls._instance = None

    # ── CLI via stdio (compatibilidade com legado) ───────────────────

    @classmethod
    def run_stdio(cls):
        """Entrypoint para rodar o servidor MCP via stdio (CLI).

        Mantido para compatibilidade com:
            python -m app.mcp.server
        """
        asyncio.run(cls._run_stdio_async())

    # ── Metodos privados ────────────────────────────────────────────

    @classmethod
    async def _run_stdio_async(cls):
        """Executa o servidor MCP com transporte stdio."""
        async with mcp.server.stdio.stdio_server() as (read, write):
            await cls.get_server().run(
                read,
                write,
                cls.get_init_options(),
            )

    @classmethod
    def _build_server(cls) -> Server:
        """Constroi e configura o servidor MCP com suas ferramentas."""
        server = Server("rag-mcp-server")
        ask_uc = AskUseCase()

        # ── Lista de ferramentas ────────────────────────────────────

        @server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="rag-ask",
                    description=(
                        "Faz perguntas aos documentos indexados no RAG "
                        "e retorna respostas com base no conteudo deles."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Pergunta sobre os documentos",
                            },
                        },
                        "required": ["question"],
                    },
                ),
                types.Tool(
                    name="rag-status",
                    description="Verifica o status do sistema RAG.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        # ── Execucao das ferramentas ────────────────────────────────

        @server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            if name == "rag-ask":
                question = (
                    arguments.get("question", "") if arguments else ""
                )
                if not question:
                    return [
                        types.TextContent(
                            type="text",
                            text="Pergunta nao informada",
                        )
                    ]

                result = ask_uc.ask(question)
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            f"Resposta: {result['answer']}\n\n"
                            f"Fontes: {len(result['sources'])} documento(s)"
                        ),
                    )
                ]

            if name == "rag-status":
                return [
                    types.TextContent(
                        type="text",
                        text="RAG MCP Server operacional",
                    )
                ]

            return [
                types.TextContent(
                    type="text",
                    text=f"Ferramenta desconhecida: {name}",
                )
            ]

        return server


# ── Entrypoint via CLI (compativel com o setup original) ────────────

if __name__ == "__main__":
    MCPServerProvider.run_stdio()
