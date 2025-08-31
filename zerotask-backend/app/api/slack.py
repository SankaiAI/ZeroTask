from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.services.slack_oauth_service import SlackOAuthService

router = APIRouter(prefix="/api/v1/slack", tags=["Slack API"])

@router.get("/channels")
async def get_channels(db: Session = Depends(get_db)):
    """Get list of channels the authenticated user has access to"""
    try:
        slack_service = SlackOAuthService(db)
        channels = slack_service.get_channels()
        return {"channels": channels}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching channels: {str(e)}")

@router.get("/messages/today")
async def get_messages_today(limit: int = 50, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get messages from today across channels"""
    try:
        slack_service = SlackOAuthService(db)
        messages = slack_service.get_messages_today(limit)
        return {
            "messages": messages,
            "count": len(messages),
            "limit": limit
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")

@router.get("/mentions/today")
async def get_mentions_today(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get messages that mention the authenticated user from today"""
    try:
        slack_service = SlackOAuthService(db)
        mentions = slack_service.get_mentions_today()
        return {
            "mentions": mentions,
            "count": len(mentions)
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mentions: {str(e)}")

@router.get("/daily-brief")
async def get_daily_brief(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get a summary of today's Slack activity"""
    try:
        slack_service = SlackOAuthService(db)
        
        # Get user info
        connection_info = slack_service.get_connection_info()
        user_info = connection_info.get('user_info', {})
        
        # Get channels
        channels = slack_service.get_channels()
        member_channels = [ch for ch in channels if ch.get('is_member')]
        
        # Get messages and mentions
        messages = slack_service.get_messages_today(30)
        mentions = slack_service.get_mentions_today()
        
        # Create summary
        summary = {
            "user": {
                "name": user_info.get('name'),
                "email": user_info.get('email')
            },
            "stats": {
                "total_channels": len(channels),
                "member_channels": len(member_channels),
                "messages_today": len(messages),
                "mentions_today": len(mentions)
            },
            "channels": [{
                "name": ch['name'],
                "is_private": ch['is_private'],
                "topic": ch['topic']
            } for ch in member_channels[:5]],  # Top 5 channels
            "recent_messages": messages[:10],  # Most recent 10 messages
            "mentions": mentions,
            "generated_at": slack_service._get_current_timestamp()
        }
        
        return summary
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating daily brief: {str(e)}")