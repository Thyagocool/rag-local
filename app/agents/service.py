"""Agente inteligente usando LangGraph com suporte a ferramentas e memória."""

from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    AIMessageChunk,
    SystemMessage,
    ToolMessage,
)
from app.config import settings
from app.agents.tools import rag_tools
import json
import logging

logger = logging.getLogger(__name__)

# ─── Estado ─────────────────────────────────────────────────────────────────


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ─── LLM ────────────────────────────────────────────────────────────────────

_llm: ChatOllama | None = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.4,
        )
    return _llm


# ─── Nós do grafo ───────────────────────────────────────────────────────────

SYSTEM_PROMPT_AGENT = """Você é um assistente inteligente que pode usar ferramentas para responder.

Suas ferramentas:
- search_documents: busca informações nos documentos indexados (RAG)
- get_current_time: diz a hora/data atual
- calculate: resolve expressões matemáticas

REGRAS:
1. Sempre responda em português
2. Use as ferramentas quando necessário
3. Se não souber, pergunte mais informações
4. Mantha as respostas claras e objetivas"""


def should_continue(state: AgentState) -> Literal["tools", END]:
    """Decide se deve continuar chamando ferramentas ou finalizar."""
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def call_model(state: AgentState):
    """Chama o LLM com as mensagens atuais."""
    llm = get_llm().bind_tools(rag_tools)
    messages = state["messages"]

    # Adiciona system prompt se não existir
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT_AGENT)] + list(messages)

    response = llm.invoke(messages)
    return {"messages": [response]}


# ─── Montagem do grafo ──────────────────────────────────────────────────────

tool_node = ToolNode(rag_tools)
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# Memória persistente em memória (dá pra trocar por SQLite depois)
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# ─── Interface ──────────────────────────────────────────────────────────────


async def run_agent_stream(message: str, thread_id: str = "default"):
    """Executa o agente com streaming token a token via SSE.

    Yields dicts com o tipo de evento:
      - token: pedaço do texto gerado pelo LLM
      - tool_call: agente chamou uma ferramenta
      - tool_result: resultado da ferramenta
      - done: sinaliza fim da execução
    """
    config = {"configurable": {"thread_id": thread_id}}
    messages = [HumanMessage(content=message)]

    input = {"messages": messages}

    # Stream em modo "messages" para capturar tokens individuais
    async for event in graph.astream(input, config, stream_mode="messages"):
        if not isinstance(event, (list, tuple)) or len(event) != 2:
            continue

        msg, metadata = event

        # Tokens do texto sendo gerado
        if isinstance(msg, AIMessageChunk) and msg.content:
            yield {"type": "token", "content": msg.content}

        # Chamadas de ferramenta
        if isinstance(msg, AIMessageChunk) and msg.tool_call_chunks:
            for tc in msg.tool_call_chunks:
                yield {
                    "type": "tool_call",
                    "name": tc.get("name", "unknown"),
                    "args": tc.get("args", "{}"),
                }

        # Resultados das ferramentas
        if isinstance(msg, ToolMessage):
            yield {
                "type": "tool_result",
                "name": getattr(msg, "name", "tool"),
                "content": msg.content[:500],
            }

        # Tool messages também podem vir como ToolMessageChunk
        if hasattr(msg, "type") and getattr(msg, "type", "") == "tool":
            yield {
                "type": "tool_result",
                "name": getattr(msg, "name", "tool"),
                "content": msg.content[:500],
            }

    yield {"type": "done"}


def run_agent(message: str, thread_id: str = "default") -> dict:
    """Executa o agente com a mensagem do usuário."""
    config = {"configurable": {"thread_id": thread_id}}
    messages = [HumanMessage(content=message)]

    steps_log = []

    # Stream dos passos do agente
    for event in graph.stream({"messages": messages}, config):
        for node_name, value in event:
            if node_name == "agent":
                msg = value["messages"][-1]
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        steps_log.append(f"Pensou -> chamou {tc['name']}")
            elif node_name == "tools":
                for msg in value.get("messages", []):
                    steps_log.append(f"Tool {msg.name}: {msg.content[:100]}...")

    # Pega a resposta final
    snapshot = graph.get_state(config)
    final_message = snapshot.values["messages"][-1]
    response = final_message.content if hasattr(final_message, "content") else str(final_message)

    return {
        "response": response,
        "thread_id": thread_id,
        "steps": steps_log,
    }


async def stream_agent_events(message: str, thread_id: str):
    """Transforma eventos do agente em eventos SSE."""
    async for event in run_agent_stream(message, thread_id):
        yield f"data: {json.dumps(event)}\n\n"
