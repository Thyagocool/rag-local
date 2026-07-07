from pydantic import BaseModel
from typing import Optional


class AgentRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"


class AgentResponse(BaseModel):
    response: str
    thread_id: str
    steps: list[str] = []
