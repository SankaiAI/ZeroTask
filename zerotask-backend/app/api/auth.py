from fastapi import APIRouter, HTTPException, status
from app.services.shared_auth_service import SharedAuthService
from app.schemas.auth import (
    TokenStoreResponse, ConnectedProvidersResponse, AuthStatusResponse,
    OAuthStartResponse
)
import httpx
from urllib.parse import urlencode

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
async def gmail_oauth_status():
    """Get Gmail OAuth configuration status"""
    try:
        client_id, client_secret = SharedAuthService.get_gmail_credentials()
        return {
            "configured": True,
            "message": "Gmail OAuth credentials configured by IT team",
            "client_id": client_id[:20] + "..." if len(client_id) > 20 else client_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))