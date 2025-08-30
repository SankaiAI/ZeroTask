from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
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

class OAuthToken(Base):
    """OAuth tokens with refresh capability for Gmail - PRD Section 8 & 9"""
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, unique=True)  # 'gmail'
    encrypted_access_token = Column(Text, nullable=False)  # AES-256 encrypted access token
    encrypted_refresh_token = Column(Text, nullable=True)  # AES-256 encrypted refresh token
    token_type = Column(String(20), default="Bearer")  # OAuth token type
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Token expiration time
    scope = Column(Text, nullable=True)  # Granted OAuth scopes
    is_active = Column(Boolean, default=True)  # Token validity status
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<OAuthToken(provider='{self.provider}', expires_at='{self.expires_at}', active={self.is_active})>"