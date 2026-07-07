"""Ferramentas que o agente pode usar."""

import math
from datetime import datetime
from langchain_core.tools import tool
from app.rag.use_cases.ask_use_case import AskUseCase
from app.agents.web_search import search_web

_ask_uc = AskUseCase()


@tool
def search_documents(query: str) -> str:
    """Busca documentos indexados no RAG e retorna respostas com base neles.
    Use para perguntas sobre os documentos que foram enviados."""
    result = _ask_uc.ask(query)
    sources = "\n".join(
        f"  - {s['content'][:200]}..."
        for s in result["sources"]
    )
    return f"Resposta: {result['answer']}\n\nFontes:\n{sources}"


@tool
def get_current_time() -> str:
    """Retorna a data e hora atual."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """Calcula uma expressao matematica. Ex: '2 + 2', 'sqrt(16)', '3 * 7'."""
    try:
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow, "int": int, "float": float,
            "sqrt": math.sqrt, "log": math.log, "log2": math.log2,
            "log10": math.log10, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "floor": math.floor, "ceil": math.ceil,
            "pi": math.pi, "e": math.e, "factorial": math.factorial,
        }
        # Permite chamadas como math.sqrt() normalizando
        expr_normalized = expression.replace("math.", "")
        result = eval(expr_normalized, {"__builtins__": {}}, allowed_names)
        # Arredonda floats longos pra 4 casas
        if isinstance(result, float):
            result = round(result, 4)
        return str(result)
    except Exception as e:
        return f"Erro ao calcular: {e}"


@tool
def search_web_tool(query: str) -> str:
    """Pesquisa na internet em tempo real. Use para perguntas sobre
    noticias atuais, eventos recentes, ou informacoes que mudam com frequencia."""
    return search_web(query)


@tool
def list_available_tools() -> str:
    """Lista todas as ferramentas disponíveis para o agente."""
    return """
Ferramentas disponiveis:
1. search_documents - Busca documentos no RAG
2. get_current_time - Mostra data/hora atual
3. calculate - Calcula expressoes matematicas
4. search_web_tool - Pesquisa na internet
5. list_available_tools - Lista as ferramentas
"""


rag_tools = [
    search_documents,
    get_current_time,
    calculate,
    search_web_tool,
    list_available_tools,
]
