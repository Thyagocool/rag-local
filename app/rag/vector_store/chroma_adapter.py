"""Adapter do ChromaDB — implementa VectorStoreAdapter."""

from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_embeddings
from app.rag.vector_store.protocol import VectorStoreAdapter
import chromadb
from chromadb.config import Settings as ChromaSettings
import os

# Desliga telemetria do ChromaDB — o posthog instalado tem API
# incompativel com a versao que o chromadb espera.
_chroma_settings = ChromaSettings(
    anonymized_telemetry=False,
)


class ChromaAdapter(VectorStoreAdapter):
    """Banco vetorial usando ChromaDB (SQLite, embedded, sem servidor)."""

    def __init__(self):
        persist_dir = settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=_chroma_settings,
        )
        self._store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=get_embeddings(),
            persist_directory=persist_dir,
            client=self._client,
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
        return [c.name for c in self._client.list_collections()]
