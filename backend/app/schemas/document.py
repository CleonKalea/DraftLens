from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UploadDocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    vectorized: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentListItem(BaseModel):
    id: int
    filename: str

class AnalyzeDocumentRequest(BaseModel):
    document_id: int

class AnalyzeDocumentResponse(BaseModel):
    response: str

class RagMetadata(BaseModel):
    total_chunks_created: int
    preview: str

class RagUploadResponse(BaseModel):
    message: str
    document_id : int
    filename: str
    rag_metadata: RagMetadata

class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]