import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.schemas.document import UploadDocumentResponse, RagUploadResponse, AnalyzeDocumentResponse, AnalyzeDocumentRequest
from app.services.document import DocumentService

router = APIRouter()

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../storage"))

# Upload Document Endpoint
@router.post("/upload", response_model=UploadDocumentResponse, status_code=status.HTTP_201_CREATED)
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
    
    document_service = DocumentService(db)

    try:
        return await document_service.save_document(file, storage_dir=STORAGE_DIR)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload pdf file to server {str(e)}"
        )
    
@router.post("/analyze-document", response_model=AnalyzeDocumentResponse, status_code=status.HTTP_200_OK)    
async def analyze_document(
    request: AnalyzeDocumentRequest,
    db: AsyncSession = Depends(get_async_db)
):
    document_service = DocumentService(db)

    try:
        return await document_service.analyze_document(document_id=request.document_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed on analyze documents function -> {str(e)}"
        )

    
@router.post("/rag/upload", response_model=RagUploadResponse, status_code=status.HTTP_201_CREATED)
async def rag_upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db)
):
    # validate
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a PDF"
        )
    
    document_service = DocumentService(db)

    try:
        rag_result = await document_service.process_document_pipeline(
            file_path=saved_document.file_path,
            document_id=saved_document.id
        )

        return {
            "message": "Document uploaded and indexed on RAG System",
            "document_id": saved_document.id,
            "filename": saved_document.filename,
            "rag_metadata": {
                "total_chunks_created": rag_result["total_chunks"],
                "preview": rag_result["sample_context_preview"]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload pdf file to server (RAG)"
        )

