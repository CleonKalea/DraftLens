from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db

from app.schemas.chat import ChatQueryRequest, ChatQueryResponse
from app.services.document import DocumentService

router = APIRouter()

@router.post("/query", response_model=ChatQueryResponse, status_code=status.HTTP_200_OK)
async def query_document(
    payload: ChatQueryRequest,
    db: AsyncSession = Depends(get_async_db)
):
    document_service = DocumentService(db)
    try:
        result = await document_service.query_document_rag(
            document_id=int(payload.document_id),
            question=payload.question
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process RAG chat: {str(e)}"
        )
    