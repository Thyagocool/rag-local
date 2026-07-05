"""Use case: fazer perguntas ao RAG (normal e streaming).

Agora com reranking opcional — re-ordena os documentos
recuperados por relevancia antes de gerar a resposta.
"""

from langchain_core.prompts import ChatPromptTemplate
from app.infra.llm import LLMFactory
from app.rag.vector_store import VectorStoreAdapter, get_vector_store_adapter
from app.config import settings
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Voce e um assistente especializado em responder perguntas com base em documentos fornecidos.

Use APENAS o contexto abaixo para responder. Se nao souber, diga que nao encontrou a informacao.

Contexto:
{context}

Pergunta: {input}

Resposta objetiva e direta:"""

RETRIEVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])


class AskUseCase:
    """Pergunta ao RAG — resposta completa ou streaming token a token."""

    def __init__(
        self,
        vector_store: VectorStoreAdapter | None = None,
        use_reranking: bool | None = None,
    ):
        self._llm = None
        self._vector_store = vector_store
        self._use_reranking = (
            settings.rag_reranking_enabled if use_reranking is None else use_reranking
        )
        self._reranker = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = LLMFactory.get_llm(temperature=0.3)
        return self._llm

    def _get_store(self) -> VectorStoreAdapter:
        if self._vector_store is None:
            self._vector_store = get_vector_store_adapter()
        return self._vector_store

    def _retrieve(self, question: str):
        """Busca documentos relevantes e monta o contexto.

        Se reranking estiver habilitado, busca mais documentos
        (k=10) e re-ordena pelos mais relevantes.
        """
        store = self._get_store()

        if self._use_reranking:
            # Busca mais docs pra dar margem pro reranker escolher
            retriever = store.as_retriever(search_kwargs={"k": 10})
            docs = retriever.invoke(question)
            from app.rag.reranking.reranker import rerank
            docs = rerank(question, docs, top_k=4)
            logger.debug("Reranking aplicado: 10 -> 4 docs")
        else:
            retriever = store.as_retriever(search_kwargs={"k": 4})
            docs = retriever.invoke(question)

        context = "\n\n".join(doc.page_content for doc in docs)
        return docs, context

    def ask(self, question: str) -> dict:
        """Faz uma pergunta ao RAG. Retorna resposta + fontes."""
        docs, context = self._retrieve(question)
        prompt = SYSTEM_PROMPT.format(context=context, input=question)
        response = self._get_llm().invoke(prompt)
        return {
            "answer": response.content,
            "sources": [
                {"content": doc.page_content[:300], "metadata": doc.metadata}
                for doc in docs
            ],
        }

    def ask_stream(self, question: str):
        """Pergunta ao RAG e retorna generator com tokens um por um (streaming).

        Reusa o mesmo _retrieve() do ask() — unico ponto de verdade.
        """
        docs, context = self._retrieve(question)
        prompt = SYSTEM_PROMPT.format(context=context, input=question)
        llm = self._get_llm()
        for chunk in llm.stream(prompt):
            if chunk.content:
                yield chunk.content
