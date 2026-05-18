import os
import shutil
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.document import DocumentRepository
from app.models import Document

class DocumentService:
    def __init__(self, db:AsyncSession):
        self.repo = DocumentRepository(db)

    async def save_and_register_document(self, file: UploadFile, storage_dir: str) -> Document:
        clean_filename = file.filename.replace(" ", "_")
        file_path = os.path.join(storage_dir, clean_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return await self.repo.create_document(filename=clean_filename, file_path=file_path)