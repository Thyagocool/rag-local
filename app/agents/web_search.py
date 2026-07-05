"""Web search tool para o agente.

Permite que o agente pesquise na internet usando DuckDuckGo.
Nao precisa de API key — 100% gratis.
"""

import logging

logger = logging.getLogger(__name__)

_MAX_RESULTS = 5


def search_web(query: str, max_results: int = _MAX_RESULTS) -> str:
    """Pesquisa na internet e retorna resultados formatados.

    Args:
        query: Termo de busca.
        max_results: Quantos resultados retornar (max 10).

    Returns:
        String formatada com titulo, snippet e URL de cada resultado.

    Raises:
        RuntimeError se a busca falhar.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        return (
            "Erro: biblioteca ddgs nao instalada. "
            "Execute: pip install ddgs"
        )

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        logger.warning("Falha na busca web: %s", e)
        return f"Erro ao pesquisar: {e}"

    if not results:
        return "Nenhum resultado encontrado."

    lines = [f"Resultados da busca por: {query}", ""]
    for i, r in enumerate(results, 1):
        title = r.get("title", "Sem titulo")
        snippet = r.get("body", "Sem descricao")
        url = r.get("href", "Sem URL")
        lines.append(f"{i}. {title}")
        lines.append(f"   {snippet[:200]}")
        lines.append(f"   Link: {url}")
        lines.append("")

    return "\n".join(lines)
