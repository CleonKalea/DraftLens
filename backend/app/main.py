from fastapi import FastAPI
from app.api.v1.endpoints.document import router as document_router
from app.api.v1.endpoints.chat import router as rag_router

app = FastAPI(title="DraftLens API", version="1.0.0")

app.include_router(document_router, prefix="/api/v1/document", tags=["Document"])
app.include_router(rag_router, prefix="/rag/chat", tags=["RAG CHAT"])

@app.get("/")
def read_root():
    return {"message": "DraftLens API!"}


