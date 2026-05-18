from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document

class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, filename:str, file_path: str) -> Document:
        new_document = Document(
            filename=filename,
            file_path=file_path,
            status = "PENDING"
        )
        self.db.add(new_document)
        await self.db.commit()
        await self.db.refresh(new_document)
        return new_document