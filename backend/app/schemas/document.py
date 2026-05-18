from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True