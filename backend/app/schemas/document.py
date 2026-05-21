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

class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]