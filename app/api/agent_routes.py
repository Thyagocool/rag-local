"""Rotas do agente — apenas roteamento, logica delegada ao agent."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import AgentRequest, AgentResponse
from app.agents.agent import run_agent, stream_agent_events

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
    """Conversa com o agente com resposta em streaming (SSE)."""
    return StreamingResponse(
        stream_agent_events(payload.message, payload.thread_id or "default"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
