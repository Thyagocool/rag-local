"""Use case: gerenciar documentos (upload, ingestao, limpeza)."""

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from fastapi import HTTPException
from app.config import settings
from app.rag.vectorstore import get_vector_store
import logging

logger = logging.getLogger(__name__)

LOADERS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
    ".docx": Docx2txtLoader,
}


def load_document(file_path: Path) -> list[Document]:
    """Carrega um documento do disco usando o loader adequado para extensao."""
    ext = file_path.suffix.lower()
    loader_cls = LOADERS.get(ext)
    if not loader_cls:
        raise HTTPException(status_code=400, detail=f"Formato nao suportado: {ext}")
    loader = loader_cls(str(file_path))
    return loader.load()


def ingest_documents(docs: list[Document]):
    """Ingere uma lista de documentos no banco vetorial."""
    vector_store = get_vector_store()
    vector_store.add_documents(docs)
    logger.info(f"{len(docs)} documento(s) ingerido(s)")


def clear_all():
    """Limpa todo o banco vetorial."""
    vector_store = get_vector_store()
    ids = vector_store.get()["ids"]
    if ids:
        vector_store.delete(ids)
        logger.info(f"{len(ids)} documento(s) removido(s)")
