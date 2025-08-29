from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Token(Base):
    """Encrypted API tokens storage - PRD Section 9 Data Model"""
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, unique=True)  # 'slack', 'github', 'gmail'
    encrypted_token = Column(Text, nullable=False)  # AES-256 encrypted token
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Token(provider='{self.provider}', created_at='{self.created_at}')>"