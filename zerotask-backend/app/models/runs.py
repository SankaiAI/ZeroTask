from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from app.database import Base

class Run(Base):
    """Brief generation runs for audit logging - PRD Section 9 Data Model"""
    __tablename__ = "runs"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default='running')  # 'running', 'completed', 'failed'
    stats_json = Column(Text, nullable=True)  # JSON with processing statistics
    error_message = Column(Text, nullable=True)  # Error details for failed runs
    
    # Index for querying recent runs
    __table_args__ = (
        Index('idx_runs_started', 'started_at'),
        Index('idx_runs_status', 'status'),
    )
    
    @property
    def duration_seconds(self) -> float:
        """Calculate run duration in seconds"""
        if not self.finished_at:
            return 0.0
        delta = self.finished_at - self.started_at
        return delta.total_seconds()
    
    def __repr__(self):
        return f"<Run(id={self.id}, status='{self.status}', started_at='{self.started_at}')>"