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
    redirect_uri: str = Field(default="http://localhost:8000/oauth2/callback")

class OAuthStartResponse(BaseModel):
    """OAuth flow initiation response"""
    authorization_url: str
    state: str

class AuthStatusResponse(BaseModel):
    """Authentication status for a provider"""
    provider: str
    connected: bool
    last_updated: Optional[datetime] = None

# Gmail-specific OAuth schemas
class GmailOAuthStartResponse(BaseModel):
    """Gmail OAuth authorization flow start response"""
    authorization_url: str = Field(..., description="Google OAuth authorization URL")
    state: str = Field(..., description="CSRF protection state parameter")
    redirect_uri: str = Field(..., description="OAuth callback URI")
    scopes: List[str] = Field(..., description="Requested Gmail scopes")

class GmailOAuthCallbackRequest(BaseModel):
    """Gmail OAuth callback parameters"""
    code: str = Field(..., description="Authorization code from Google")
    state: str = Field(..., description="State parameter for CSRF validation")
    scope: Optional[str] = Field(None, description="Granted scopes from Google")

class GmailOAuthCallbackResponse(BaseModel):
    """Gmail OAuth callback processing response"""
    success: bool = Field(..., description="OAuth flow success status")
    message: str = Field(..., description="Human-readable status message")
    user_email: Optional[str] = Field(None, description="Authenticated user email")
    scopes: Optional[List[str]] = Field(None, description="Granted OAuth scopes")
    expires_at: Optional[str] = Field(None, description="Token expiration timestamp")

class GmailConnectionStatusResponse(BaseModel):
    """Gmail OAuth connection status response"""
    configured: bool = Field(..., description="OAuth credentials configured by IT")
    authenticated: bool = Field(..., description="User has completed OAuth flow")
    message: str = Field(..., description="Status message")
    user_email: Optional[str] = Field(None, description="Connected Gmail account")
    scopes: Optional[List[str]] = Field(None, description="Current OAuth scopes")
    expires_at: Optional[str] = Field(None, description="Token expiration")
    client_id_preview: Optional[str] = Field(None, description="Preview of OAuth client ID")

class GmailOAuthRevokeResponse(BaseModel):
    """Gmail OAuth revocation response"""
    success: bool = Field(..., description="Revocation success status")
    message: str = Field(..., description="Revocation status message")