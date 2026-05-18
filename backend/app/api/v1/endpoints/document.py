import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService

router = APIRouter()

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../storage"))

# Upload Document Endpoint
@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db)
):
    # Validate .pdf file extension
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a PDF"
        )
    doc_service = DocumentService(db)
    try:
        return await doc_service.save_and_register_document(file, storage_dir=STORAGE_DIR)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload pdf file to server {str(e)}"
        )
    

