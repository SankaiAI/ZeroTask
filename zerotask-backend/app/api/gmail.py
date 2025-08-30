"""
Gmail API Router for ZeroTask - PRD Section 8 Implementation

This router provides Gmail API endpoints for the daily brief system.
It handles email reading, draft creation, and search functionality
while maintaining the local-first architecture.

Key Endpoints:
- GET /emails/recent - Get recent Gmail messages
- GET /emails/today - Get today's messages for daily brief
- GET /threads/important - Get important email threads
- POST /drafts/reply - Create Gmail draft reply
- GET /search - Search Gmail messages
- GET /labels - Get Gmail labels for filtering
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.services.gmail_api_service import GmailApiService
from app.services.gmail_oauth_service import GmailOAuthService
from pydantic import BaseModel, Field


class GmailSearchRequest(BaseModel):
    """Gmail search request"""
    query: str = Field(..., description="Gmail search query")
    max_results: int = Field(default=20, le=100, description="Maximum results to return")


class GmailDraftRequest(BaseModel):
    """Gmail draft creation request"""
    message_id: str = Field(..., description="ID of message to reply to")
    content: str = Field(..., description="Draft reply content")
    subject_prefix: str = Field(default="Re: ", description="Subject prefix for reply")


class GmailMessageResponse(BaseModel):
    """Gmail message response"""
    id: str
    thread_id: str
    subject: str
    from_email: str = Field(alias="from")
    to_email: str = Field(alias="to")
    date: str
    snippet: str
    web_link: str
    body: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class GmailThreadResponse(BaseModel):
    """Gmail thread response"""
    thread_id: str
    subject: str
    participants: List[str]
    message_count: int
    last_message_date: str
    snippet: str
    web_link: str
    messages: List[GmailMessageResponse]


class GmailDraftResponse(BaseModel):
    """Gmail draft creation response"""
    success: bool
    draft_id: Optional[str] = None
    message: str
    gmail_link: Optional[str] = None
    thread_id: Optional[str] = None
    subject: Optional[str] = None
    recipient: Optional[str] = None


class GmailLabelResponse(BaseModel):
    """Gmail label response"""
    id: str
    name: str
    type: str
    messages_total: int
    messages_unread: int


router = APIRouter(tags=["Gmail API - Email Management"])


@router.get("/profile")
async def get_gmail_profile(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get Gmail user profile and account information
    
    Returns user email, message counts, and account details.
    """
    try:
        profile = await GmailApiService.get_user_profile(db)
        return {
            "success": True,
            "profile": profile
        }
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Gmail profile: {str(e)}"
        )


@router.get("/emails/recent")
async def get_recent_emails(
    db: Session = Depends(get_db),
    max_results: int = Query(default=50, le=100, description="Maximum number of emails"),
    query: Optional[str] = Query(None, description="Gmail search query"),
    label_ids: Optional[str] = Query(None, description="Comma-separated label IDs")
) -> Dict[str, Any]:
    """
    Get recent Gmail messages with optional filtering
    
    Supports Gmail search query syntax and label filtering.
    Used by daily brief system to fetch relevant emails.
    """
    try:
        label_list = label_ids.split(',') if label_ids else None
        
        messages = await GmailApiService.get_recent_messages(
            db=db,
            max_results=max_results,
            query=query,
            label_ids=label_list
        )
        
        return {
            "success": True,
            "count": len(messages),
            "messages": messages,
            "query": query,
            "max_results": max_results
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recent emails: {str(e)}"
        )


@router.get("/emails/today")
async def get_today_emails(
    db: Session = Depends(get_db),
    max_results: int = Query(default=50, le=100, description="Maximum number of emails")
) -> Dict[str, Any]:
    """
    Get today's Gmail messages - PRD Section 8 requirement
    
    This endpoint is specifically designed for the daily brief system
    to fetch emails received today for summarization.
    """
    try:
        messages = await GmailApiService.get_today_messages(
            db=db,
            max_results=max_results
        )
        
        return {
            "success": True,
            "count": len(messages),
            "messages": messages,
            "date": datetime.now().date().isoformat(),
            "brief_ready": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting today's emails: {str(e)}"
        )


@router.get("/threads/important")
async def get_important_threads(
    db: Session = Depends(get_db),
    days_back: int = Query(default=7, le=30, description="Days to look back for threads")
) -> Dict[str, Any]:
    """
    Get important email threads - PRD Section 8 requirement
    
    Fetches important, starred, and sent email threads from recent days.
    Used by daily brief to identify ongoing important conversations.
    """
    try:
        threads = await GmailApiService.get_important_threads(
            db=db,
            days_back=days_back
        )
        
        return {
            "success": True,
            "count": len(threads),
            "threads": threads,
            "days_back": days_back,
            "brief_ready": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting important threads: {str(e)}"
        )


@router.get("/thread/{thread_id}")
async def get_thread_details(
    thread_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a Gmail thread
    
    Returns all messages in the thread with full context.
    """
    try:
        thread = await GmailApiService.get_thread(db, thread_id)
        
        if not thread:
            raise HTTPException(
                status_code=404,
                detail=f"Thread {thread_id} not found"
            )
        
        return {
            "success": True,
            "thread": thread
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting thread details: {str(e)}"
        )


@router.post("/drafts/reply", response_model=GmailDraftResponse)
async def create_draft_reply(
    request: GmailDraftRequest,
    db: Session = Depends(get_db)
) -> GmailDraftResponse:
    """
    Create a Gmail draft reply - PRD Section 8 requirement
    
    Creates a draft reply to an existing email message.
    User must review and send the draft in Gmail interface.
    """
    try:
        result = await GmailApiService.create_draft_reply(
            db=db,
            message_id=request.message_id,
            draft_content=request.content,
            subject_prefix=request.subject_prefix
        )
        
        return GmailDraftResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating draft reply: {str(e)}"
        )


@router.post("/search")
async def search_emails(
    request: GmailSearchRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search Gmail messages using Gmail query syntax
    
    Supports advanced search queries like:
    - "from:example@company.com"
    - "subject:project is:unread"
    - "has:attachment after:2024/01/01"
    """
    try:
        messages = await GmailApiService.search_emails(
            db=db,
            query=request.query,
            max_results=request.max_results
        )
        
        return {
            "success": True,
            "count": len(messages),
            "messages": messages,
            "query": request.query
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching emails: {str(e)}"
        )


@router.get("/labels", response_model=List[GmailLabelResponse])
async def get_gmail_labels(db: Session = Depends(get_db)) -> List[GmailLabelResponse]:
    """
    Get Gmail labels for filtering and organization
    
    Returns all available labels including system labels (INBOX, SENT)
    and user-created labels for filtering emails.
    """
    try:
        labels = await GmailApiService.get_labels(db)
        return [GmailLabelResponse(**label) for label in labels]
        
    except ValueError as e:
        raise HTTPException(
            status_code=401 if "not authenticated" in str(e) else 400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Gmail labels: {str(e)}"
        )


@router.get("/connection/status")
async def get_gmail_connection_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive Gmail connection status
    
    Returns OAuth configuration status, authentication status,
    and connection health information.
    """
    try:
        status = await GmailOAuthService.get_connection_status(db)
        
        # Add additional connection health check
        if status["authenticated"]:
            try:
                profile = await GmailApiService.get_user_profile(db)
                status["connection_health"] = "healthy"
                status["last_check"] = datetime.now().isoformat()
                status["api_accessible"] = True
            except Exception as e:
                status["connection_health"] = "degraded"
                status["connection_error"] = str(e)
                status["api_accessible"] = False
        else:
            status["connection_health"] = "not_connected"
            status["api_accessible"] = False
            
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking Gmail connection status: {str(e)}"
        )