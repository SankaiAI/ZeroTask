import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from app.models.tokens import OAuthToken
from app.config import settings
from app.utils.encryption import token_encryption

class GmailOAuthService:
    """Gmail OAuth 2.0 service for secure token management - PRD Section 8"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose'
    ]
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_authorization_url(self) -> tuple[str, str]:
        """Generate OAuth authorization URL with secure state - PRD Section 8"""
        if not settings.google_client_id or not settings.google_client_secret:
            raise ValueError("Google OAuth credentials not configured by IT team")
        
        # Create flow with redirect to localhost
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8000/oauth2/callback"]
                }
            },
            scopes=self.SCOPES,
            redirect_uri="http://localhost:8000/oauth2/callback"
        )
        
        # Generate secure state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',  # Enable refresh tokens
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent screen to get refresh token
        )
        
        return auth_url, state
    
    def exchange_code_for_tokens(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for OAuth tokens - PRD Section 8"""
        if not settings.google_client_id or not settings.google_client_secret:
            raise ValueError("Google OAuth credentials not configured by IT team")
        
        # Create flow for token exchange
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8000/oauth2/callback"]
                }
            },
            scopes=self.SCOPES,
            state=state,
            redirect_uri="http://localhost:8000/oauth2/callback"
        )
        
        # Exchange authorization code for tokens
        flow.fetch_token(code=code)
        
        # Extract token information
        credentials = flow.credentials
        token_info = {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_type': 'Bearer',
            'expires_at': credentials.expiry,
            'scope': ' '.join(credentials.scopes) if credentials.scopes else ' '.join(self.SCOPES)
        }
        
        # Store encrypted tokens in database
        self._store_oauth_tokens(token_info)
        
        return token_info
    
    def _store_oauth_tokens(self, token_info: Dict[str, Any]) -> None:
        """Store encrypted OAuth tokens in database - PRD Section 11 Security"""
        try:
            # Encrypt tokens
            encrypted_access_token = token_encryption.encrypt_token(token_info['access_token'])
            encrypted_refresh_token = None
            if token_info.get('refresh_token'):
                encrypted_refresh_token = token_encryption.encrypt_token(token_info['refresh_token'])
            
            # Check for existing token
            existing_token = self.db.query(OAuthToken).filter(OAuthToken.provider == 'gmail').first()
            
            if existing_token:
                # Update existing token
                existing_token.encrypted_access_token = encrypted_access_token
                existing_token.encrypted_refresh_token = encrypted_refresh_token
                existing_token.token_type = token_info.get('token_type', 'Bearer')
                existing_token.expires_at = token_info.get('expires_at')
                existing_token.scope = token_info.get('scope')
                existing_token.is_active = True
                existing_token.updated_at = datetime.now(timezone.utc)
            else:
                # Create new token record
                new_token = OAuthToken(
                    provider='gmail',
                    encrypted_access_token=encrypted_access_token,
                    encrypted_refresh_token=encrypted_refresh_token,
                    token_type=token_info.get('token_type', 'Bearer'),
                    expires_at=token_info.get('expires_at'),
                    scope=token_info.get('scope'),
                    is_active=True
                )
                self.db.add(new_token)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to store OAuth tokens: {str(e)}")
    
    def get_valid_credentials(self) -> Optional[Credentials]:
        """Get valid Gmail credentials, refreshing if necessary - PRD Section 8"""
        token_record = self.db.query(OAuthToken).filter(
            OAuthToken.provider == 'gmail',
            OAuthToken.is_active == True
        ).first()
        
        if not token_record:
            return None
        
        try:
            # Decrypt tokens
            access_token = token_encryption.decrypt_token(token_record.encrypted_access_token)
            refresh_token = None
            if token_record.encrypted_refresh_token:
                refresh_token = token_encryption.decrypt_token(token_record.encrypted_refresh_token)
            
            # Create credentials object
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                scopes=token_record.scope.split(' ') if token_record.scope else self.SCOPES
            )
            
            # Check if token needs refresh
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Update stored tokens with refreshed values
                self._update_refreshed_token(token_record, credentials)
            
            return credentials
            
        except Exception as e:
            # Mark token as inactive if decryption/refresh fails
            token_record.is_active = False
            self.db.commit()
            raise ValueError(f"Failed to get valid credentials: {str(e)}")
    
    def _update_refreshed_token(self, token_record: OAuthToken, credentials: Credentials) -> None:
        """Update database with refreshed token - PRD Section 8"""
        try:
            # Encrypt new access token
            token_record.encrypted_access_token = token_encryption.encrypt_token(credentials.token)
            
            # Update refresh token if provided
            if credentials.refresh_token:
                token_record.encrypted_refresh_token = token_encryption.encrypt_token(credentials.refresh_token)
            
            # Update expiration time
            token_record.expires_at = credentials.expiry
            token_record.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update refreshed token: {str(e)}")
    
    def revoke_tokens(self) -> bool:
        """Revoke OAuth tokens and remove from database - PRD Section 11"""
        try:
            credentials = self.get_valid_credentials()
            
            if credentials and credentials.token:
                # Revoke token with Google
                import requests
                revoke_url = 'https://oauth2.googleapis.com/revoke'
                requests.post(revoke_url, params={'token': credentials.token})
            
            # Remove from database
            token_record = self.db.query(OAuthToken).filter(OAuthToken.provider == 'gmail').first()
            if token_record:
                self.db.delete(token_record)
                self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to revoke tokens: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Gmail is connected with valid tokens"""
        try:
            credentials = self.get_valid_credentials()
            return credentials is not None and not credentials.expired
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get Gmail connection status information"""
        token_record = self.db.query(OAuthToken).filter(
            OAuthToken.provider == 'gmail',
            OAuthToken.is_active == True
        ).first()
        
        if not token_record:
            return {
                'connected': False,
                'status': 'Not connected',
                'scopes': None,
                'expires_at': None
            }
        
        try:
            credentials = self.get_valid_credentials()
            return {
                'connected': True,
                'status': 'Connected' if not credentials.expired else 'Token expired',
                'scopes': token_record.scope.split(' ') if token_record.scope else [],
                'expires_at': token_record.expires_at.isoformat() if token_record.expires_at else None,
                'created_at': token_record.created_at.isoformat()
            }
        except:
            return {
                'connected': False,
                'status': 'Connection error',
                'scopes': None,
                'expires_at': None
            }