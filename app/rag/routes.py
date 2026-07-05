"""Rotas do RAG — apenas roteamento, logica delegada ao service."""

import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from app.rag.schemas import (
    AskRequest,
    AskResponse,
    Source,
    UploadResponse,
)
from app.rag.service import (
    ask,
    stream_answer,
    load_document,
    LOADERS,
    ingest_documents,
    clear_all,
)

router = APIRouter()


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
        stream_answer(payload.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


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
        docs = load_document(Path(tmp_path))
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
