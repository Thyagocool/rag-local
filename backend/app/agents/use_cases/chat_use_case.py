"""Use case: conversar com o agente (normal e streaming)."""

from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    AIMessageChunk,
    SystemMessage,
    ToolMessage,
)
from app.infra.llm import LLMFactory
from app.agents.tools import rag_tools
import logging

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


SYSTEM_PROMPT_AGENT = """Voce e um assistente inteligente que pode usar ferramentas para responder.

Suas ferramentas:
- search_documents: busca informacoes nos documentos indexados (RAG)
- get_current_time: diz a hora/data atual
- calculate: resolve expressoes matematicas

REGRAS:
1. Sempre responda em portugues
2. Use as ferramentas quando necessario
3. Se nao souber, pergunte mais informacoes
4. Mantenha as respostas claras e objetivas
5. Nao repita informacoes. Seja conciso.
6. NUNCA inclua JSON de ferramentas nem definicoes de parametros na sua resposta. As ferramentas sao chamadas internamente, sem mostrar o JSON ao usuario."""


class ChatUseCase:
    """Conversa com o agente — resposta completa ou streaming com tool calls."""

    def __init__(self):
        self._llm = None
        self._graph = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = LLMFactory.get_llm(temperature=0.4)
        return self._llm

    def _get_graph(self):
        if self._graph is None:
            llm = self._get_llm().bind_tools(rag_tools)

            def call_model(state: AgentState):
                messages = state["messages"]
                if not any(isinstance(m, SystemMessage) for m in messages):
                    messages = [SystemMessage(content=SYSTEM_PROMPT_AGENT)] + list(messages)
                response = llm.invoke(messages)
                return {"messages": [response]}

            def should_continue(state: AgentState) -> Literal["tools", END]:
                last_message = state["messages"][-1]
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    return "tools"
                return END

            tool_node = ToolNode(rag_tools)
            workflow = StateGraph(AgentState)
            workflow.add_node("agent", call_model)
            workflow.add_node("tools", tool_node)
            workflow.set_entry_point("agent")
            workflow.add_conditional_edges("agent", should_continue)
            workflow.add_edge("tools", "agent")

            memory = MemorySaver()
            self._graph = workflow.compile(checkpointer=memory)
        return self._graph

    def run_agent(self, message: str, thread_id: str = "default") -> dict:
        """Executa o agente com a mensagem do usuario."""
        graph = self._get_graph()
        config = {"configurable": {"thread_id": thread_id}}
        messages = [HumanMessage(content=message)]

        steps_log = []
        for event in graph.stream({"messages": messages}, config):
            for node_name, value in event.items() if isinstance(event, dict) else event:
                if node_name == "agent":
                    msg = value["messages"][-1]
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            steps_log.append(f"Pensou -> chamou {tc['name']}")
                elif node_name == "tools":
                    for msg in value.get("messages", []):
                        steps_log.append(f"Tool {msg.name}: {msg.content[:100]}...")

        snapshot = graph.get_state(config)
        final_message = snapshot.values["messages"][-1]
        response = final_message.content if hasattr(final_message, "content") else str(final_message)

        return {
            "response": response,
            "thread_id": thread_id,
            "steps": steps_log,
        }

    async def run_agent_stream(self, message: str, thread_id: str = "default"):
        """Executa o agente com streaming — tokens, tool_calls e tool_results.

        Usa stream_mode='updates' para evitar vazar JSON bruto de tool calls.
        """
        graph = self._get_graph()
        config = {"configurable": {"thread_id": thread_id}}
        messages = [HumanMessage(content=message)]

        last_token_sent = None
        async for event in graph.astream(
            {"messages": messages}, config, stream_mode="updates"
        ):
            if not isinstance(event, dict):
                continue

            for node_name, value in event.items():
                if value is None:
                    continue

                node_messages = value.get("messages", [])
                if not node_messages:
                    continue

                last_msg = node_messages[-1]

                if node_name == "agent":
                    if isinstance(last_msg, AIMessage):
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            for tc in last_msg.tool_calls:
                                yield {
                                    "type": "tool_call",
                                    "name": tc.get("name", "unknown"),
                                    "args": tc.get("args", "{}"),
                                }
                        elif last_msg.content:
                            content = last_msg.content
                            # Evita emitir o mesmo token duas vezes
                            if content != last_token_sent:
                                last_token_sent = content
                                yield {
                                    "type": "token",
                                    "content": content,
                                }

                elif node_name == "tools":
                    for msg in node_messages:
                        yield {
                            "type": "tool_result",
                            "name": getattr(msg, "name", "tool"),
                            "content": msg.content[:500],
                        }

        yield {"type": "done"}
# Exports pra manter compatibilidade com codigo legado
# (tools.py e mcp/server.py importam direto)
