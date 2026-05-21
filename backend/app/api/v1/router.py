from fastapi import APIRouter
from app.api.v1.endpoints.document import router as document_router
from app.api.v1.endpoints.chat import router as rag_router

api_router = APIRouter()

api_router.include_router(document_router, prefix="/document", tags=["Document"])

api_router.include_router(rag_router, prefix="/rag/chat", tags=["RAG CHAT"])