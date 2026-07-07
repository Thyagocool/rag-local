"""Fabrica compartilhada de LLM — evita duplicacao de configuracao."""

from langchain_ollama import ChatOllama
from app.config import settings


class LLMFactory:
    """Cria (ou reusa) instancias de ChatOllama.

    Cacheia por temperatura para evitar recriar.
    Se quiser forcar recriacao (ex: .env mudou), chame LLMFactory.reset().
    """

    _instances: dict[str, ChatOllama] = {}

    @classmethod
    def get_llm(cls, temperature: float = 0.3) -> ChatOllama:
        key = str(temperature)
        if key not in cls._instances:
            cls._instances[key] = ChatOllama(
                model=settings.llm_model,
                base_url=settings.ollama_base_url,
                temperature=temperature,
            )
        return cls._instances[key]

    @classmethod
    def reset(cls):
        """Limpa o cache — util em testes ou reload de config."""
        cls._instances.clear()
