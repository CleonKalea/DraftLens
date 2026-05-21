from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.db.session import Base
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    vectorized = Column(Integer, default=0)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime, default=datetime.now)
