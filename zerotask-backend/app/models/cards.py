from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Card(Base):
    """Daily brief cards with LLM-generated summaries - PRD Section 9 Data Model"""
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    primary_event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    priority_score = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    summary_md = Column(Text, nullable=False)  # Markdown-formatted summary
    evidence_links = Column(Text, nullable=True)  # JSON array of URLs with snippets
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    snoozed_until = Column(DateTime(timezone=True), nullable=True)  # For snooze functionality
    
    # Relationship to primary event
    primary_event = relationship("Event", back_populates="cards")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_cards_priority', 'priority_score'),
        Index('idx_cards_created', 'created_at'),
        Index('idx_cards_snoozed', 'snoozed_until'),
    )
    
    @property
    def is_snoozed(self) -> bool:
        """Check if card is currently snoozed"""
        if not self.snoozed_until:
            return False
        from datetime import datetime
        return datetime.utcnow() < self.snoozed_until.replace(tzinfo=None)
    
    def __repr__(self):
        return f"<Card(id={self.id}, priority={self.priority_score}, created_at='{self.created_at}')>"