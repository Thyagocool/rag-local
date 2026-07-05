"""Adapter do ChromaDB — implementa VectorStoreAdapter."""

import chromadb
from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_embeddings
from app.rag.vector_store.protocol import VectorStoreAdapter
import os


class ChromaAdapter(VectorStoreAdapter):
    """Banco vetorial usando ChromaDB (SQLite, embedded, sem servidor)."""

    def __init__(self):
        persist_dir = settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self._store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=get_embeddings(),
            persist_directory=persist_dir,
        )

    def as_retriever(self, **kwargs):
        return self._store.as_retriever(**kwargs)

    def add_documents(self, docs):
        self._store.add_documents(docs)

    def clear_all(self):
        ids = self._store.get()["ids"]
        if ids:
            self._store.delete(ids)

    def list_collections(self) -> list[str]:
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        return [c.name for c in client.list_collections()]
