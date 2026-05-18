from fastapi import FastAPI
from app.api.v1.endpoints.document import router as document_router

app = FastAPI(title="DraftLens API", version="1.0.0")

app.include_router(document_router, prefix="/api/v1/document", tags=["Document"])

@app.get("/")
def read_root():
    return {"message": "DraftLens API!"}