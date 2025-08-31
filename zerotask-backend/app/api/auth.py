from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.shared_auth_service import SharedAuthService
from app.services.gmail_oauth_service import GmailOAuthService
from app.services.slack_oauth_service import SlackOAuthService
from app.schemas.auth import (
    TokenStoreResponse, ConnectedProvidersResponse, AuthStatusResponse,
    OAuthStartResponse, GmailOAuthStartResponse, GmailOAuthCallbackRequest,
    GmailOAuthCallbackResponse, GmailConnectionStatusResponse, GmailOAuthRevokeResponse
)
import httpx
from urllib.parse import urlencode
from typing import Optional

router = APIRouter(tags=["Authentication - Shared Service Accounts"])

@router.get("/status/{provider}", response_model=AuthStatusResponse)
async def get_auth_status(provider: str):
    """Get IT-configured authentication status for a provider - PRD Section 10"""
    if provider not in ['slack', 'github', 'gmail']:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid provider: {provider}"
        )
    
    status = SharedAuthService.get_connection_status()
    provider_status = status.get(provider, {"configured": False})
    
    return AuthStatusResponse(
        provider=provider,
        connected=provider_status["configured"]
    )

@router.get("/providers", response_model=ConnectedProvidersResponse)
async def get_connected_providers():
    """Get list of IT-configured providers"""
    status = SharedAuthService.get_connection_status()
    configured_providers = [
        provider for provider, config in status.items() 
        if config["configured"]
    ]
    
    return ConnectedProvidersResponse(
        providers=configured_providers,
        count=len(configured_providers)
    )

@router.get("/validate")
async def validate_service_accounts():
    """Validate all IT-configured service accounts - PRD Section 10"""
    validation = SharedAuthService.validate_all_connections()
    
    if validation["all_configured"]:
        status_code = 200
        message = "All service accounts configured by IT team"
    else:
        status_code = 206  # Partial Content
        message = f"Only {validation['configured_services']}/{validation['total_services']} services configured"
    
    return {
        "status_code": status_code,
        "message": message,
        "validation": validation
    }

@router.get("/github/test")
async def test_github_connection():
    """Test GitHub service account connection"""
    try:
        token = SharedAuthService.get_github_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "GitHub service account connected successfully",
                    "user": user_data.get("login", "Unknown")
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail="GitHub service account token invalid"
                )
                
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except httpx.RequestError:
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to GitHub API"
        )

@router.get("/slack/test")
async def test_slack_connection():
    """Test Slack service account connection"""
    try:
        app_token, bot_token = SharedAuthService.get_slack_tokens()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/auth.test",
                headers={"Authorization": f"Bearer {bot_token}"}
            )
            
            data = response.json()
            if data.get("ok"):
                return {
                    "success": True,
                    "message": "Slack service account connected successfully",
                    "team": data.get("team", "Unknown"),
                    "user": data.get("user", "Unknown")
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Slack service account invalid: {data.get('error', 'Unknown error')}"
                )
                
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except httpx.RequestError:
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to Slack API"
        )

@router.get("/gmail/status")
async def gmail_oauth_status(db: Session = Depends(get_db)):
    """Get Gmail OAuth configuration status"""
    try:
        # Check if OAuth credentials are configured by IT team
        from app.config import settings
        oauth_configured = bool(settings.google_client_id and settings.google_client_secret)
        
        if not oauth_configured:
            return {
                "configured": False,
                "message": "Gmail OAuth credentials not configured by IT team",
                "scopes": None,
                "expires_at": None
            }
        
        # OAuth is configured, check user connection status
        gmail_service = GmailOAuthService(db)
        info = gmail_service.get_connection_info()
        return {
            "configured": True,  # OAuth credentials are configured by IT
            "authenticated": info['connected'],  # User has completed OAuth flow
            "message": info['status'],
            "scopes": info.get('scopes', []),
            "expires_at": info.get('expires_at')
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking Gmail status: {str(e)}"
        )

# Gmail OAuth 2.0 Flow Endpoints - PRD Section 8
@router.get("/gmail/oauth/start")
async def start_gmail_oauth(db: Session = Depends(get_db)):
    """Start Gmail OAuth 2.0 Desktop flow - PRD Section 8"""
    from app.config import settings
    
    print("=== Gmail OAuth Start Debug ===")
    print(f"Client ID: {settings.google_client_id[:20]}...{settings.google_client_id[-10:]}")
    print(f"Client Secret configured: {bool(settings.google_client_secret)}")
    print(f"Client Secret length: {len(settings.google_client_secret) if settings.google_client_secret else 0}")
    
    try:
        gmail_service = GmailOAuthService(db)
        auth_url, state = gmail_service.get_authorization_url()
        
        print(f"Generated Auth URL: {auth_url[:100]}...")
        print(f"Generated State: {state}")
        print(f"Redirect URI: http://localhost:8000/oauth2/callback")
        
        # Test the auth URL construction
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(auth_url)
        query_params = parse_qs(parsed_url.query)
        
        print("=== OAuth URL Analysis ===")
        print(f"Base URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}")
        print(f"Client ID in URL: {query_params.get('client_id', ['None'])[0]}")
        print(f"Response Type: {query_params.get('response_type', ['None'])[0]}")
        print(f"Scope: {query_params.get('scope', ['None'])[0]}")
        print(f"Redirect URI in URL: {query_params.get('redirect_uri', ['None'])[0]}")
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "redirect_uri": "http://localhost:8000/oauth2/callback",
            "scopes": ["gmail.readonly", "gmail.compose"]
        }
    except ValueError as e:
        print(f"ValueError in OAuth start: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting Gmail OAuth: {str(e)}"
        )

@router.get("/oauth2/callback")
async def gmail_oauth_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Handle Gmail OAuth 2.0 callback - PRD Section 8"""
    # Handle OAuth errors
    if error:
        return RedirectResponse(
            url=f"http://localhost:3000/?gmail_error={error}",
            status_code=302
        )
    
    if not code or not state:
        return RedirectResponse(
            url="http://localhost:3000/?gmail_error=Missing code or state",
            status_code=302
        )
    
    try:
        gmail_service = GmailOAuthService(db)
        token_info = gmail_service.exchange_code_for_tokens(code, state)
        
        # Redirect to frontend with success
        return RedirectResponse(
            url="http://localhost:3000/?gmail_success=true",
            status_code=302
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"http://localhost:3000/?gmail_error=OAuth failed: {str(e)}",
            status_code=302
        )

@router.post("/gmail/oauth/revoke")
async def revoke_gmail_oauth(db: Session = Depends(get_db)):
    """Revoke Gmail OAuth access and clean up tokens"""
    try:
        gmail_service = GmailOAuthService(db)
        success = gmail_service.revoke_tokens()
        
        return {
            "success": success,
            "message": "Gmail OAuth access revoked successfully" if success else "No tokens to revoke"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error revoking Gmail OAuth: {str(e)}"
        )

@router.get("/gmail/test")
async def test_gmail_connection(db: Session = Depends(get_db)):
    """Test Gmail API connection with current OAuth tokens"""
    try:
        gmail_service = GmailOAuthService(db)
        credentials = gmail_service.get_valid_credentials()
        
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Gmail not authenticated. Complete OAuth flow first."
            )
        
        # Test Gmail API access
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers={"Authorization": f"Bearer {credentials.token}"}
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                return {
                    "success": True,
                    "message": "Gmail connection test successful",
                    "email": profile_data.get("emailAddress"),
                    "total_messages": profile_data.get("messagesTotal", 0)
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Gmail API test failed: {response.status_code}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing Gmail connection: {str(e)}"
        )

# Slack Individual OAuth 2.0 Flow Endpoints
@router.get("/slack/oauth/status")
async def slack_oauth_status(db: Session = Depends(get_db)):
    """Get Slack OAuth configuration status"""
    try:
        from app.config import settings
        oauth_configured = bool(settings.slack_client_id and settings.slack_client_secret)
        
        if not oauth_configured:
            return {
                "configured": False,
                "message": "Slack OAuth credentials not configured by IT team",
                "scopes": None,
                "expires_at": None
            }
        
        slack_service = SlackOAuthService(db)
        info = slack_service.get_connection_info()
        return {
            "configured": True,
            "authenticated": info['connected'],
            "message": info['status'],
            "scopes": info.get('scopes', []),
            "expires_at": info.get('expires_at'),
            "user_info": info.get('user_info', {})
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking Slack status: {str(e)}"
        )

@router.get("/slack/oauth/start")
async def start_slack_oauth(db: Session = Depends(get_db)):
    """Start Slack OAuth 2.0 flow"""
    from app.config import settings
    
    try:
        slack_service = SlackOAuthService(db)
        auth_url, state = slack_service.get_authorization_url()
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "redirect_uri": "https://1012d16f9d68.ngrok-free.app/oauth2/slack/callback",
            "scopes": SlackOAuthService.SCOPES
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting Slack OAuth: {str(e)}"
        )

@router.get("/oauth2/slack/callback")
async def slack_oauth_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Handle Slack OAuth 2.0 callback"""
    if error:
        return RedirectResponse(
            url=f"http://localhost:3001/oauth-error.html?slack_error={error}",
            status_code=302
        )
    
    if not code or not state:
        return RedirectResponse(
            url="http://localhost:3001/oauth-error.html?slack_error=Missing code or state",
            status_code=302
        )
    
    try:
        slack_service = SlackOAuthService(db)
        token_info = slack_service.exchange_code_for_tokens(code, state)
        
        return RedirectResponse(
            url="http://localhost:3001/oauth-success.html",
            status_code=302
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"http://localhost:3001/oauth-error.html?slack_error=OAuth failed: {str(e)}",
            status_code=302
        )

@router.post("/slack/oauth/revoke")
async def revoke_slack_oauth(db: Session = Depends(get_db)):
    """Revoke Slack OAuth access and clean up tokens"""
    try:
        slack_service = SlackOAuthService(db)
        success = slack_service.revoke_tokens()
        
        return {
            "success": success,
            "message": "Slack OAuth access revoked successfully" if success else "No tokens to revoke"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error revoking Slack OAuth: {str(e)}"
        )

@router.get("/slack/oauth/test")
async def test_slack_oauth_connection(db: Session = Depends(get_db)):
    """Test Slack API connection with current OAuth tokens"""
    try:
        slack_service = SlackOAuthService(db)
        access_token = slack_service.get_valid_credentials()
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="Slack not authenticated. Complete OAuth flow first."
            )
        
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/auth.test",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            data = response.json()
            if data.get("ok"):
                return {
                    "success": True,
                    "message": "Slack OAuth connection test successful",
                    "user": data.get("user", "Unknown"),
                    "team": data.get("team", "Unknown")
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Slack API test failed: {data.get('error', 'Unknown error')}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing Slack OAuth connection: {str(e)}"
        )