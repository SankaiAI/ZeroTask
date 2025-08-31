from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from app.config import settings
from app.database import create_tables
from app.api import health, auth, gmail, slack

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("Starting ZeroTask API...")
    print(f"Database: {settings.database_url}")
    print(f"LLM: {settings.ollama_base_url}/{settings.ollama_model}")
    
    # Create database tables
    create_tables()
    print("Database tables created/verified")
    
    # TODO: Start background job scheduler
    print("Background jobs initialized")
    
    yield
    
    # Shutdown
    print("Shutting down ZeroTask API...")
    # TODO: Shutdown background job scheduler

# Create FastAPI application with lifespan
app = FastAPI(
    title="ZeroTask API",
    description="Local-first daily brief system for Gmail, Slack & GitHub",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(gmail.router, prefix="/api/v1/gmail")
app.include_router(slack.router)

# OAuth callback endpoints (no prefix for external redirects)
@app.get("/oauth2/callback")
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handle OAuth 2.0 callbacks from external providers"""
    import logging
    from fastapi import Query, Depends, HTTPException
    from fastapi.responses import RedirectResponse
    from sqlalchemy.orm import Session
    from app.database import get_db
    from app.services.gmail_oauth_service import GmailOAuthService
    from typing import Optional
    
    # Debug logging
    print("=== OAuth Callback Received ===")
    print(f"Code: {'YES' if code else 'NO'} ({'[REDACTED]' if code else 'None'})")
    print(f"State: {state[:10] + '...' if state and len(state) > 10 else state}")
    print(f"Error: {error}")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Handle OAuth errors
        if error:
            print(f"OAUTH ERROR: {error}")
            return RedirectResponse(
                url=f"http://localhost:3001/?gmail_error={error}",
                status_code=302
            )
        
        if not code or not state:
            print(f"MISSING PARAMS - Code: {bool(code)}, State: {bool(state)}")
            return RedirectResponse(
                url="http://localhost:3001/?gmail_error=Missing code or state",
                status_code=302
            )
        
        print("Processing Gmail OAuth token exchange...")
        
        # Process Gmail OAuth callback
        gmail_service = GmailOAuthService(db)
        token_info = gmail_service.exchange_code_for_tokens(code, state)
        
        print("SUCCESS: Gmail OAuth token exchange completed")
        
        # Redirect to frontend with success
        return RedirectResponse(
            url="http://localhost:3001/?gmail_success=true",
            status_code=302
        )
        
    except Exception as e:
        print(f"CALLBACK ERROR: {str(e)}")
        return RedirectResponse(
            url=f"http://localhost:3001/?gmail_error=OAuth failed: {str(e)}",
            status_code=302
        )
    finally:
        db.close()

@app.get("/oauth2/slack/callback")
async def slack_oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handle Slack OAuth 2.0 callback"""
    from fastapi.responses import RedirectResponse
    from sqlalchemy.orm import Session
    from app.database import get_db
    from app.services.slack_oauth_service import SlackOAuthService
    
    # Debug logging
    print("=== Slack OAuth Callback Received ===")
    print(f"Code: {'YES' if code else 'NO'}")
    print(f"State: {state[:10] + '...' if state and len(state) > 10 else state}")
    print(f"Error: {error}")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Handle OAuth errors
        if error:
            print(f"SLACK OAUTH ERROR: {error}")
            return RedirectResponse(
                url=f"http://localhost:3001/?slack_error={error}",
                status_code=302
            )
        
        if not code or not state:
            print(f"MISSING PARAMS - Code: {bool(code)}, State: {bool(state)}")
            return RedirectResponse(
                url="http://localhost:3001/?slack_error=Missing code or state",
                status_code=302
            )
        
        print("Processing Slack OAuth token exchange...")
        
        # Process Slack OAuth callback
        slack_service = SlackOAuthService(db)
        token_info = slack_service.exchange_code_for_tokens(code, state)
        
        print("SUCCESS: Slack OAuth token exchange completed")
        
        # Redirect to frontend with success
        return RedirectResponse(
            url="http://localhost:3001/?slack_success=true",
            status_code=302
        )
        
    except Exception as e:
        print(f"SLACK CALLBACK ERROR: {str(e)}")
        return RedirectResponse(
            url=f"http://localhost:3001/?slack_error=OAuth failed: {str(e)}",
            status_code=302
        )
    finally:
        db.close()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ZeroTask API - Local-first daily brief system",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs" if settings.debug else None
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )