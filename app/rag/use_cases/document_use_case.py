"""Use case: gerenciar documentos (upload, ingestao, limpeza)."""

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from app.rag.vector_store import VectorStoreAdapter, get_vector_store_adapter
import logging

logger = logging.getLogger(__name__)


class DocumentUseCase:
    """Upload, ingestao e limpeza de documentos no banco vetorial."""

    LOADERS = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".md": TextLoader,
        ".docx": Docx2txtLoader,
    }

    def __init__(self, vector_store: VectorStoreAdapter | None = None):
        self._vector_store = vector_store

    def _get_store(self) -> VectorStoreAdapter:
        if self._vector_store is None:
            self._vector_store = get_vector_store_adapter()
        return self._vector_store

    def load_document(self, file_path: Path) -> list[Document]:
        """Carrega um documento do disco usando o loader adequado."""
        ext = file_path.suffix.lower()
        loader_cls = self.LOADERS.get(ext)
        if not loader_cls:
            raise ValueError(f"Formato nao suportado: {ext}")
        loader = loader_cls(str(file_path))
        return loader.load()

    def ingest_documents(self, docs: list[Document]):
        """Ingere documentos no banco vetorial."""
        store = self._get_store()
        store.add_documents(docs)
        logger.info(f"{len(docs)} documento(s) ingerido(s)")

    def clear_all(self):
        """Limpa todo o banco vetorial."""
        store = self._get_store()
        store.clear_all()
        logger.info("Banco vetorial limpo")
