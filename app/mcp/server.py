"""Servidor MCP (Model Context Protocol) para expor ferramentas do RAG.

O MCP permite que qualquer cliente compatível (incluindo agents do Claude,
Cline, etc.) consuma as tools do nosso sistema remotamente.
"""

import asyncio
import logging
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from app.rag.service import ask as rag_ask

logger = logging.getLogger(__name__)

server = Server("rag-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Lista as ferramentas expostas via MCP."""
    return [
        types.Tool(
            name="rag-ask",
            description="Faz perguntas aos documentos indexados no RAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Pergunta sobre os documentos"},
                },
                "required": ["question"],
            },
        ),
        types.Tool(
            name="rag-status",
            description="Verifica o status do sistema RAG",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Executa uma ferramenta MCP."""
    if name == "rag-ask":
        question = arguments.get("question", "") if arguments else ""
        if not question:
            return [types.TextContent(type="text", text=" Pergunta não informada")]

        result = rag_ask(question)
        return [
            types.TextContent(
                type="text",
                text=f"Resposta: {result['answer']}\n\n"
                     f"Fontes: {len(result['sources'])} documento(s)",
            )
        ]

    elif name == "rag-status":
        return [
            types.TextContent(
                type="text",
                text="RAG MCP Server operacional",
            )
        ]

    else:
        return [types.TextContent(type="text", text=f"Ferramenta desconhecida: {name}")]


async def run_mcp_server():
    """Roda o servidor MCP via stdio (compatível com Claude Desktop, Cline etc.)."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rag-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def start_mcp():
    """Entrypoint para rodar o MCP server."""
    asyncio.run(run_mcp_server())


if __name__ == "__main__":
    start_mcp()
