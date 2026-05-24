from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ChatQueryRequest(BaseModel):
    document_id: int
    question: str

class ChatQueryResponse(BaseModel):
    answer: str
    # source_chunks: List[str]

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    document_id: int
    title: Optional[str] = "New Chat"

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    document_id: int
    created_at: datetime

    # model_config = ConfigDict(from_attributes=True)
    class Config:
        from_attributes = True


class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[MessageResponse] = []
