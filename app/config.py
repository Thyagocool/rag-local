from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Ollama ---
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"

    # --- ChromaDB ---
    chroma_persist_dir: str = "./data/chroma"
    collection_name: str = "rag_docs"

    # --- App ---
    app_name: str = "RAG + Agentes + MCP"
    app_version: str = "0.1.0"
    debug: bool = True

    # --- Agentes ---
    max_tool_calls: int = 5

    model_config = {"env_prefix": "RAG_", "env_file": ".env"}


settings = Settings()
