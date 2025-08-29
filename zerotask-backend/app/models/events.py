from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Event(Base):
    """Source events (Slack, GitHub, Gmail) - PRD Section 9 Data Model"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)  # 'slack', 'github', 'gmail'
    source_id = Column(String(255), nullable=False)  # External ID from source API
    url = Column(Text, nullable=True)  # Deep link to original item
    title = Column(Text, nullable=False)
    snippet = Column(Text, nullable=True)  # Content preview
    author = Column(String(255), nullable=True)
    ts = Column(DateTime(timezone=True), nullable=False)  # Event timestamp from source
    raw_json = Column(Text, nullable=True)  # Original API response for debugging
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to cards that reference this event
    cards = relationship("Card", back_populates="primary_event")
    
    # Unique constraint to prevent duplicate events
    __table_args__ = (
        Index('idx_events_source_id', 'source', 'source_id', unique=True),
        Index('idx_events_source_ts', 'source', 'ts'),
        Index('idx_events_ts', 'ts'),
    )
    
    def __repr__(self):
        return f"<Event(source='{self.source}', title='{self.title[:50]}...', ts='{self.ts}')>"