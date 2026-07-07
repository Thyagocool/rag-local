"""Reranking de documentos usando cross-encoder.

Melhora a qualidade das respostas re-ordenando os documentos
recuperados pelo similarity search. O cross-encoder avalia
a relevancia de cada documento em relacao a pergunta.
"""

import logging
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

# Modelo tiny de cross-encoder (~80MB, roda em CPU)
DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"

_reranker: CrossEncoder | None = None


def get_reranker(model_name: str = DEFAULT_MODEL) -> CrossEncoder:
    """Retorna instancia do cross-encoder (cacheada)."""
    global _reranker
    if _reranker is None:
        logger.info("Carregando reranker: %s...", model_name)
        _reranker = CrossEncoder(model_name, max_length=512)
        logger.info("Reranker pronto")
    return _reranker


def rerank(
    query: str,
    documents: list,
    top_k: int = 4,
    model_name: str = DEFAULT_MODEL,
) -> list:
    """Re-ordena documentos por relevancia a pergunta.

    Args:
        query: Pergunta do usuario.
        documents: Lista de Document do LangChain.
        top_k: Quantos documentos retornar depois do rerank.
        model_name: Nome do modelo cross-encoder.

    Returns:
        Lista dos top_k documentos re-ordenados (mais relevante primeiro).
    """
    if not documents:
        return documents

    model = get_reranker(model_name)

    # Prepara pares (pergunta, conteudo) pro cross-encoder
    pairs = [(query, doc.page_content) for doc in documents]

    # Cross-encoder retorna scores de relevancia
    scores = model.predict(pairs)

    # Junta scores com documentos e ordena
    scored = list(zip(scores, documents))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Retorna os top_k mais relevantes
    reranked = [doc for _, doc in scored[:top_k]]

    logger.debug(
        "Rerank: %d docs -> scores %s -> top %d",
        len(documents),
        [round(float(s), 3) for s in sorted(scores, reverse=True)],
        top_k,
    )

    return reranked
