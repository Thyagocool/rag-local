"""Use case: fazer perguntas ao RAG (normal e streaming)."""

import json
from langchain_ollama import ChatOllama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.rag.vectorstore import get_vector_store
import logging

logger = logging.getLogger(__name__)

# --- Prompts ---

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

# --- Singleton do LLM ---

_llm: ChatOllama | None = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.3,
        )
    return _llm


def create_rag_chain():
    """Monta a chain RAG completa: busca nos docs + geracao da resposta."""
    llm = get_llm()
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    combine_docs_chain = create_stuff_documents_chain(llm, RETRIEVAL_PROMPT)
    chain = create_retrieval_chain(retriever, combine_docs_chain)

    return chain


def ask(question: str) -> dict:
    """Faz uma pergunta ao RAG. Retorna resposta + fontes."""
    chain = create_rag_chain()
    result = chain.invoke({"input": question})
    return {
        "answer": result["answer"],
        "sources": [
            {"content": doc.page_content[:300], "metadata": doc.metadata}
            for doc in result.get("context", [])
        ],
    }


def ask_stream(question: str):
    """Pergunta ao RAG e retorna um generator com tokens um por um (streaming)."""
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = SYSTEM_PROMPT.format(context=context, input=question)

    llm = get_llm()
    for chunk in llm.stream(prompt):
        if chunk.content:
            yield chunk.content


def stream_answer(question: str):
    """Faz pergunta ao RAG e retorna generator de eventos SSE (token a token)."""
    for token in ask_stream(question):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"
