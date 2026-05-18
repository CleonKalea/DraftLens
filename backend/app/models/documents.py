from sqlalchemy import Column, Integer, String, DateTime
from app.db.session import Base
from datetime import datetime

class Documents(Base):
    __tablename__ = "Documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime, default=datetime.now())
    