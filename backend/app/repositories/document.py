from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
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
    
    async def get_document(self, document_id: int) -> Document | None:
        query =  select(Document).where(Document.id == document_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_vectorized_status(self, document_id: int) -> bool:
        query = (
            update(Document)
            .where(Document.id == document_id)
            .values(vectorized=1)
            )
        
        result = await self.db.execute(query)
        await self.db.commit()
