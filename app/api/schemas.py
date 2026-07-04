from pydantic import BaseModel
from typing import Optional


class Source(BaseModel):
    content: str
    metadata: dict


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class AskRequest(BaseModel):
    question: str


class UploadResponse(BaseModel):
    message: str
    documents_processed: int


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class AgentRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"


class AgentResponse(BaseModel):
    response: str
    thread_id: str
    steps: list[str] = []


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str
    vector_collections: list[str]
