from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from typing import List
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatSessionCreate, ChatSessionDetailResponse, ChatSessionResponse, MessageResponse
from app.services.document import DocumentService
from app.services.chat import ChatServices

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
    
@router.post("/query/stream")
async def handle_query(
    session_id: int, 
    user_question: str, 
    db: AsyncSession = Depends(get_async_db)
):
    chat_service = ChatServices(db)

    try:
        stream_generator = chat_service.query_response_stream(session_id, user_question)

        return StreamingResponse(
            stream_generator, 
            media_type="text/event-stream"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer chat: {str(e)}"
        )

# Create new chat session
@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatSessionCreate,
    db: AsyncSession = Depends(get_async_db)
    ):

    chat_services = ChatServices(db)

    try:
        new_session = await chat_services.create_chat_session(
            document_id=payload.document_id,
            title=payload.title
            )
        return new_session
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create new session: {str(e)}"
        )
    
@router.get("/sessions/{document_id}", response_model=List[ChatSessionResponse], status_code=status.HTTP_200_OK)
async def get_chat_sessions(
    document_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    chat_services = ChatServices(db)

    try:
        return await chat_services.get_chat_sessions(document_id=document_id)
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to Retrieve Session: {str(e)}")
    
@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse], status_code=status.HTTP_200_OK)
async def get_session_messages(
    session_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    chat_services = ChatServices(db)

    try:
        return await chat_services.get_session_messages(session_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to Retrieve Messages: {str(e)}")
    
