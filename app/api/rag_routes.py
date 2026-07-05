"""Rotas do RAG — perguntar, fazer upload e limpar documentos."""

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
)
from app.rag.engine import ask, ask_stream, ingest_documents, clear_all

router = APIRouter()

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
        raise HTTPException(status_code=400, detail=f"Formato nao suportado: {ext}")
    loader = loader_cls(str(file_path))
    return loader.load()


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
    """Faz uma pergunta ao RAG com resposta em streaming (SSE)."""
    return StreamingResponse(
        _stream_answer(payload.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _stream_answer(question: str):
    """Transforma tokens do RAG em eventos SSE."""
    for token in ask_stream(question):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Faz upload de um documento (PDF, TXT, MD, DOCX) para indexar no RAG."""
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename nao informado")

    ext = Path(file.filename).suffix.lower()
    if ext not in LOADERS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato nao suportado. Use: {', '.join(LOADERS.keys())}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        docs = _load_document(Path(tmp_path))
        ingest_documents(docs)
        return UploadResponse(
            message=f"{file.filename} indexado com sucesso!",
            documents_processed=len(docs),
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.delete("/clear")
def clear_vector_store():
    """Remove todos os documentos do banco vetorial."""
    clear_all()
    return {"message": "Banco vetorial limpo!"}
