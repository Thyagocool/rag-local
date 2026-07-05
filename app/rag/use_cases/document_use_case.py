"""Use case: gerenciar documentos (upload, ingestao, limpeza)."""

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from app.rag.vectorstore import get_vector_store
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
        vector_store = get_vector_store()
        vector_store.add_documents(docs)
        logger.info(f"{len(docs)} documento(s) ingerido(s)")

    def clear_all(self):
        """Limpa todo o banco vetorial."""
        vector_store = get_vector_store()
        ids = vector_store.get()["ids"]
        if ids:
            vector_store.delete(ids)
            logger.info(f"{len(ids)} documento(s) removido(s)")
