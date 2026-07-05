"""Rotas do agente — conversa normal e com streaming."""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import AgentRequest, AgentResponse
from app.agents.agent import run_agent, run_agent_stream

router = APIRouter()


@router.post("/agent", response_model=AgentResponse)
def chat_with_agent(payload: AgentRequest):
    """Conversa com o agente (que pode usar RAG + ferramentas)."""
    try:
        result = run_agent(payload.message, thread_id=payload.thread_id)
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


async def _stream_agent_events(message: str, thread_id: str):
    """Transforma eventos do agente em SSE."""
    async for event in run_agent_stream(message, thread_id):
        yield f"data: {json.dumps(event)}\n\n"
