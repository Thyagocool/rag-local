"""Wrapper do ChromaDB — banco vetorial free e persistente.

NOTA: ChromaDB usa SQLite internamente. Nao precisa "fechar" conexao.
Manter uma unica instancia (singleton) e seguro e mais performatico
do que criar uma nova a cada request.
"""

import chromadb
from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_embeddings
import os

_vector_store: Chroma | None = None


def get_vector_store() -> Chroma:
    """Retorna o vector store ChromaDB (cacheado apos primeira criacao).

    O Chroma gerencia conexao internamente — nao ha risco de estourar
    sessoes como aconteceria com um banco relacional tradicional.
    """
    global _vector_store
    if _vector_store is None:
        persist_dir = settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        _vector_store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=get_embeddings(),
            persist_directory=persist_dir,
        )
    return _vector_store


def list_collections() -> list[str]:
    """Lista as colecoes disponiveis no ChromaDB."""
    persist_dir = settings.chroma_persist_dir
    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    return [c.name for c in client.list_collections()]
