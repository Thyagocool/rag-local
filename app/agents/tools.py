"""Ferramentas que o agente pode usar."""

from langchain_core.tools import tool
from app.rag.engine import ask as rag_ask
from datetime import datetime
import json


@tool
def search_documents(query: str) -> str:
    """Busca documentos indexados no RAG e retorna respostas com base neles.
    Use para perguntas sobre os documentos que foram enviados."""
    result = rag_ask(query)
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
    """Calcula uma expressão matemática. Ex: '2 + 2', 'sqrt(16)', '3 * 7'."""
    try:
        # Avaliação segura — sem builtins perigosos
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow, "int": int, "float": float,
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Resultado: {result}"
    except Exception as e:
        return f"Erro ao calcular: {e}"


@tool
def list_available_tools() -> str:
    """Lista todas as ferramentas disponíveis para o agente."""
    return """
Ferramentas disponiveis:
1. search_documents - Busca documentos no RAG
2. get_current_time - Mostra data/hora atual
3. calculate - Calcula expressoes matematicas
4. list_available_tools - Lista as ferramentas
"""


rag_tools = [search_documents, get_current_time, calculate, list_available_tools]
