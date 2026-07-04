"""Wrapper do ChromaDB — banco vetorial free e persistente."""

import chromadb
from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_embeddings
import os


def get_vector_store() -> Chroma:
    """Retorna (ou cria) o vector store ChromaDB persistido em disco."""
    persist_dir = settings.chroma_persist_dir
    os.makedirs(persist_dir, exist_ok=True)

    vector_store = Chroma(
        collection_name=settings.collection_name,
        embedding_function=get_embeddings(),
        persist_directory=persist_dir,
    )
    return vector_store


def list_collections() -> list[str]:
    """Lista as coleções disponíveis no ChromaDB."""
    persist_dir = settings.chroma_persist_dir
    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    return [c.name for c in client.list_collections()]
