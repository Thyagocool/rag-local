"""Protocolo abstrato para o banco vetorial.

Permite trocar de implementacao (ChromaDB, pgvector, Pinecone...)
sem modificar o codigo dos use cases — so criar um novo adapter.
"""

from abc import ABC, abstractmethod
from langchain_core.documents import Document


class VectorStoreAdapter(ABC):
    """Interface que qualquer banco vetorial precisa implementar."""

    @abstractmethod
    def as_retriever(self, **kwargs):
        """Retorna um retriever configurado para buscas de similaridade."""
        ...

    @abstractmethod
    def add_documents(self, docs: list[Document]):
        """Adiciona documentos ao banco vetorial."""
        ...

    @abstractmethod
    def clear_all(self):
        """Remove todos os documentos do banco."""
        ...

    @abstractmethod
    def list_collections(self) -> list[str]:
        """Lista as colecoes/disponiveis."""
        ...
