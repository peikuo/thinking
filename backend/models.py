from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# Request models used across the application
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    language: Optional[str] = "en"
    stream: Optional[bool] = True

class SummaryRequest(BaseModel):
    responses: Dict[str, str]
    question: str
    language: Optional[str] = "en"
    stream: Optional[bool] = True
