from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.database import get_db
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint - PRD Section 16.2 API Endpoints"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # TODO: Test Ollama connection
    llm_status = "not_implemented"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "services": {
            "database": db_status,
            "llm": llm_status,
        },
        "config": {
            "ollama_url": settings.ollama_base_url,
            "model": settings.ollama_model,
            "debug": settings.debug
        }
    }