from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TokenStoreRequest(BaseModel):
    """Request to store a token for a provider"""
    provider: str = Field(..., description="Provider name (slack, github, gmail)")
    token: str = Field(..., description="API token to store")

class TokenStoreResponse(BaseModel):
    """Response after storing a token"""
    success: bool
    message: str
    provider: str

class ConnectedProvidersResponse(BaseModel):
    """List of connected providers"""
    providers: List[str]
    count: int

class GitHubConnectRequest(BaseModel):
    """GitHub Personal Access Token connection"""
    token: str = Field(..., description="GitHub Personal Access Token")

class SlackConnectRequest(BaseModel):
    """Slack Socket Mode connection"""
    app_token: str = Field(..., description="Slack App Token (xapp-...)")
    bot_token: str = Field(..., description="Slack Bot Token (xoxb-...)")

class GmailOAuthRequest(BaseModel):
    """Gmail OAuth authorization request"""
    authorization_code: str = Field(..., description="OAuth authorization code")
    redirect_uri: str = Field(default="http://localhost:8000/auth/gmail/callback")

class OAuthStartResponse(BaseModel):
    """OAuth flow initiation response"""
    authorization_url: str
    state: str

class AuthStatusResponse(BaseModel):
    """Authentication status for a provider"""
    provider: str
    connected: bool
    last_updated: Optional[datetime] = None