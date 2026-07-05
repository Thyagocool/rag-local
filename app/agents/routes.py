"""Rotas do agente — apenas roteamento, logica delegada aos use cases."""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.schemas import AgentRequest, AgentResponse
from app.agents.use_cases.chat_use_case import ChatUseCase

chat_uc = ChatUseCase()

router = APIRouter()


# ─── Helpers de streaming (presentation) ───────────────────────────────


async def _stream_agent_events(message: str, thread_id: str):
    """Converte eventos do agente em eventos SSE."""
    async for event in chat_uc.run_agent_stream(message, thread_id):
        yield f"data: {json.dumps(event)}\n\n"


# ─── Rotas ─────────────────────────────────────────────────────────────


@router.post("/agent", response_model=AgentResponse)
def chat_with_agent(payload: AgentRequest):
    """Conversa com o agente (que pode usar RAG + ferramentas)."""
    try:
        result = chat_uc.run_agent(payload.message, thread_id=payload.thread_id)
        return AgentResponse(
            response=result["response"],
            thread_id=result["thread_id"],
            steps=result.get("steps", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/stream")
async def agent_stream(payload: AgentRequest):
    """Conversa com o agente com resposta em streaming (SSE).

    Retorna eventos de token, tool_call, tool_result em tempo real.
    """
    return StreamingResponse(
        _stream_agent_events(payload.message, payload.thread_id or "default"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
