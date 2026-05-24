from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ChatSession, Message
from typing import List
from sqlalchemy import select

class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_new_session(self, document_id: int, title: str) -> ChatSession:
        new_session = ChatSession(
            title=title,
            document_id=document_id
        )

        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)

        return new_session
    
    async def get_chat_sessions(self, document_id: int) -> List[ChatSession]:
        query = (
            select(ChatSession).
            where(ChatSession.document_id == document_id).
            order_by(ChatSession.created_at.desc())
            )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_session_messages(self, session_id: int) -> List[Message]:
        query = (
            select(Message).
            where(Message.session_id == session_id).
            order_by(Message.created_at.asc())
        )

        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def save_message(self, session_id: int, role: str, content: str) -> Message:
        query = Message(
            session_id=session_id,
            role=role,
            content=content
        )

        self.db.add(query)
        await self.db.commit()
        await self.db.refresh(query)

    async def get_session_by_id(self, session_id: int) -> ChatSession:
        query = (
            select(ChatSession).
            where(ChatSession.id == session_id)
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()