from pydantic import BaseModel
from typing import List

class ChatQueryRequest(BaseModel):
    document_id: int
    question: str

class ChatQueryResponse(BaseModel):
    answer: str
    # source_chunks: List[str]

