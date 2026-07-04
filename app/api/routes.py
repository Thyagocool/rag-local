"""Rotas da API REST — RAG, Agentes, Upload e Saúde."""

import json
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)

from app.api.schemas import (
    AskRequest,
    AskResponse,
    Source,
    UploadResponse,
    AgentRequest,
    AgentResponse,
    HealthResponse,
)
from app.rag.engine import ask, ask_stream, ingest_documents, clear_all
from app.rag.vectorstore import list_collections
from app.agents.agent import run_agent
from app.config import settings

router = APIRouter()

# ─── Suporte ────────────────────────────────────────────────────────────────

LOADERS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
    ".docx": Docx2txtLoader,
}


def _load_document(file_path: Path) -> list[Document]:
    ext = file_path.suffix.lower()
    loader_cls = LOADERS.get(ext)
    if not loader_cls:
        raise HTTPException(status_code=400, detail=f"Formato não suportado: {ext}")
    loader = loader_cls(str(file_path))
    return loader.load()


# ─── RAG ────────────────────────────────────────────────────────────────────


@router.post("/ask", response_model=AskResponse)
def ask_rag(payload: AskRequest):
    """Faz uma pergunta ao RAG com base nos documentos indexados."""
    try:
        result = ask(payload.question)
        return AskResponse(
            answer=result["answer"],
            sources=[Source(**s) for s in result["sources"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask/stream")
def ask_rag_stream(payload: AskRequest):
    """Faz uma pergunta ao RAG com resposta em streaming (SSE - Server-Sent Events).

    Retorna tokens um por um conforme o LLM gera a resposta.
    Use `EventSource` no frontend ou `curl -N` pra consumir.
    """
    return StreamingResponse(
        _stream_answer(payload.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _stream_answer(question: str):
    """Generator que transforma tokens do RAG em eventos SSE."""
    for token in ask_stream(question):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Faz upload de um documento (PDF, TXT, MD, DOCX) para indexar no RAG."""
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename não informado")

    ext = Path(file.filename).suffix.lower()
    if ext not in LOADERS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado. Use: {', '.join(LOADERS.keys())}",
        )

    # Salva temporário e carrega
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        docs = _load_document(Path(tmp_path))
        ingest_documents(docs)
        return UploadResponse(
            message=f"✅ {file.filename} indexado com sucesso!",
            documents_processed=len(docs),
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.delete("/clear")
def clear_vector_store():
    """Remove todos os documentos do banco vetorial."""
    clear_all()
    return {"message": "🧹 Banco vetorial limpo!"}


# ─── Agentes ────────────────────────────────────────────────────────────────


@router.post("/agent", response_model=AgentResponse)
def chat_with_agent(payload: AgentRequest):
    """Conversa com o agente (que pode usar RAG + ferramentas)."""
    try:
        result = run_agent(payload.message, thread_id=payload.thread_id)
        return AgentResponse(
            response=result["response"],
            thread_id=result["thread_id"],
            steps=result.get("steps", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Utilitários ────────────────────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check do serviço."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        vector_collections=list_collections(),
    )
