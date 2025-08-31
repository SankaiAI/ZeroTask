import secrets
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import httpx

from app.models.tokens import OAuthToken
from app.config import settings
from app.utils.encryption import token_encryption

class SlackOAuthService:
    """Slack OAuth 2.0 service for individual user connections"""
    
    SCOPES = [
        'channels:read',
        'chat:write', 
        'users:read',
        'users:read.email',
        'channels:history',
        'groups:read',
        'im:read',
        'search:read'
    ]
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_authorization_url(self) -> tuple[str, str]:
        """Generate Slack OAuth authorization URL with secure state"""
        if not settings.slack_client_id or not settings.slack_client_secret:
            raise ValueError("Slack OAuth credentials not configured by IT team")
        
        # Generate secure state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Build Slack OAuth URL
        params = {
            'client_id': settings.slack_client_id,
            'scope': ' '.join(self.SCOPES),
            'redirect_uri': 'https://1012d16f9d68.ngrok-free.app/oauth2/slack/callback',
            'state': state,
            'response_type': 'code'
        }
        
        from urllib.parse import urlencode
        auth_url = 'https://slack.com/oauth/v2/authorize?' + urlencode(params)
        
        return auth_url, state
    
    def exchange_code_for_tokens(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for Slack OAuth tokens"""
        if not settings.slack_client_id or not settings.slack_client_secret:
            raise ValueError("Slack OAuth credentials not configured by IT team")
        
        # Exchange code for token
        token_url = 'https://slack.com/api/oauth.v2.access'
        data = {
            'client_id': settings.slack_client_id,
            'client_secret': settings.slack_client_secret,
            'code': code,
            'redirect_uri': 'https://1012d16f9d68.ngrok-free.app/oauth2/slack/callback'
        }
        
        response = httpx.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        print(f"=== Slack OAuth Response Debug ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {token_data}")
        
        if not token_data.get('ok'):
            raise ValueError(f"Slack OAuth failed: {token_data.get('error', 'Unknown error')}")
        
        # Extract token information - check structure
        if 'authed_user' in token_data and 'access_token' in token_data['authed_user']:
            access_token = token_data['authed_user']['access_token']
        elif 'access_token' in token_data:
            access_token = token_data['access_token']
        else:
            raise ValueError(f"No access_token found in response. Available keys: {list(token_data.keys())}")
            
        user_id = token_data.get('authed_user', {}).get('id', 'unknown')
        team_name = token_data.get('team', {}).get('name', 'unknown')
        
        # Fetch user profile information using the access token
        user_profile = self._fetch_user_profile(access_token, user_id)
        
        token_info = {
            'access_token': access_token,
            'user_id': user_id,
            'team_name': team_name,
            'scope': ' '.join(self.SCOPES),
            'token_type': 'Bearer',
            'user_profile': user_profile
        }
        
        # Store encrypted tokens in database
        self._store_oauth_tokens(token_info)
        
        return token_info
    
    def _fetch_user_profile(self, access_token: str, user_id: str) -> Dict[str, Any]:
        """Fetch user profile information from Slack API"""
        try:
            # Use users.info API to get user profile
            profile_url = 'https://slack.com/api/users.info'
            response = httpx.get(
                profile_url,
                headers={'Authorization': f'Bearer {access_token}'},
                params={'user': user_id}
            )
            response.raise_for_status()
            
            profile_data = response.json()
            if not profile_data.get('ok'):
                print(f"Failed to fetch user profile: {profile_data.get('error', 'Unknown error')}")
                return {}
            
            user = profile_data.get('user', {})
            profile = user.get('profile', {})
            
            return {
                'user_id': user.get('id'),
                'name': profile.get('real_name') or profile.get('display_name') or user.get('name'),
                'email': profile.get('email'),
                'avatar_url': profile.get('image_512') or profile.get('image_192') or profile.get('image_72'),
                'title': profile.get('title'),
                'team_id': user.get('team_id'),
                'is_admin': user.get('is_admin', False),
                'timezone': user.get('tz_label')
            }
            
        except Exception as e:
            print(f"Error fetching user profile: {str(e)}")
            return {}
    
    def _store_oauth_tokens(self, token_info: Dict[str, Any]) -> None:
        """Store encrypted Slack OAuth tokens in database"""
        try:
            # Encrypt tokens
            encrypted_access_token = token_encryption.encrypt_token(token_info['access_token'])
            
            # Serialize user profile information as JSON
            import json
            user_info_json = json.dumps(token_info.get('user_profile', {}))
            
            # Check for existing token
            existing_token = self.db.query(OAuthToken).filter(OAuthToken.provider == 'slack').first()
            
            if existing_token:
                # Update existing token
                existing_token.encrypted_access_token = encrypted_access_token
                existing_token.encrypted_refresh_token = None  # Slack doesn't use refresh tokens
                existing_token.token_type = token_info.get('token_type', 'Bearer')
                existing_token.expires_at = None  # Slack tokens don't expire
                existing_token.scope = token_info.get('scope')
                existing_token.user_info = user_info_json
                existing_token.is_active = True
                existing_token.updated_at = datetime.now(timezone.utc)
            else:
                # Create new token record
                new_token = OAuthToken(
                    provider='slack',
                    encrypted_access_token=encrypted_access_token,
                    encrypted_refresh_token=None,
                    token_type=token_info.get('token_type', 'Bearer'),
                    expires_at=None,  # Slack tokens don't expire
                    scope=token_info.get('scope'),
                    user_info=user_info_json,
                    is_active=True
                )
                self.db.add(new_token)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to store Slack OAuth tokens: {str(e)}")
    
    def get_valid_credentials(self) -> Optional[str]:
        """Get valid Slack credentials (access token)"""
        token_record = self.db.query(OAuthToken).filter(
            OAuthToken.provider == 'slack',
            OAuthToken.is_active == True
        ).first()
        
        if not token_record:
            return None
        
        try:
            # Decrypt token
            access_token = token_encryption.decrypt_token(token_record.encrypted_access_token)
            return access_token
            
        except Exception as e:
            # Mark token as inactive if decryption fails
            token_record.is_active = False
            self.db.commit()
            raise ValueError(f"Failed to get valid credentials: {str(e)}")
    
    def revoke_tokens(self) -> bool:
        """Revoke Slack OAuth tokens and remove from database"""
        try:
            access_token = self.get_valid_credentials()
            
            if access_token:
                # Revoke token with Slack
                revoke_url = 'https://slack.com/api/auth.revoke'
                response = httpx.post(revoke_url, headers={'Authorization': f'Bearer {access_token}'})
                # Note: Slack auth.revoke might not be available for user tokens, but we'll try
            
            # Remove from database
            token_record = self.db.query(OAuthToken).filter(OAuthToken.provider == 'slack').first()
            if token_record:
                self.db.delete(token_record)
                self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to revoke tokens: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Slack is connected with valid tokens"""
        try:
            credentials = self.get_valid_credentials()
            return credentials is not None
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get Slack connection status information"""
        token_record = self.db.query(OAuthToken).filter(
            OAuthToken.provider == 'slack',
            OAuthToken.is_active == True
        ).first()
        
        if not token_record:
            return {
                'connected': False,
                'status': 'Not connected',
                'scopes': None,
                'user_info': None
            }
        
        try:
            access_token = self.get_valid_credentials()
            
            # Parse user info from stored JSON
            import json
            user_info = {}
            if token_record.user_info:
                try:
                    user_info = json.loads(token_record.user_info)
                    print(f"=== User Info Debug ===")
                    print(f"Raw user_info from DB: {token_record.user_info}")
                    print(f"Parsed user_info: {user_info}")
                except json.JSONDecodeError:
                    print(f"JSON decode error for user_info: {token_record.user_info}")
                    user_info = {}
            else:
                print(f"No user_info found in token record")
            
            return {
                'connected': True,
                'status': 'Connected',
                'scopes': token_record.scope.split(' ') if token_record.scope else [],
                'created_at': token_record.created_at.isoformat(),
                'user_info': user_info
            }
        except Exception as e:
            print(f"Exception in get_connection_info: {str(e)}")
            return {
                'connected': False,
                'status': 'Connection error',
                'scopes': None,
                'user_info': None
            }
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """Get list of channels the user has access to"""
        access_token = self.get_valid_credentials()
        if not access_token:
            raise ValueError("Not authenticated with Slack")
        
        try:
            response = httpx.get(
                'https://slack.com/api/conversations.list',
                headers={'Authorization': f'Bearer {access_token}'},
                params={'types': 'public_channel,private_channel'}
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('ok'):
                raise ValueError(f"Slack API error: {data.get('error', 'Unknown error')}")
            
            channels = []
            for channel in data.get('channels', []):
                channels.append({
                    'id': channel.get('id'),
                    'name': channel.get('name'),
                    'is_private': channel.get('is_private', False),
                    'is_member': channel.get('is_member', False),
                    'topic': channel.get('topic', {}).get('value', ''),
                    'purpose': channel.get('purpose', {}).get('value', '')
                })
            
            return channels
            
        except Exception as e:
            raise ValueError(f"Failed to fetch channels: {str(e)}")
    
    def get_messages_today(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages from today across channels the user has access to"""
        access_token = self.get_valid_credentials()
        if not access_token:
            raise ValueError("Not authenticated with Slack")
        
        # Get today's timestamp range
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_timestamp = today.timestamp()
        
        try:
            # First get channels
            channels = self.get_channels()
            # Try all accessible channels, not just member channels (since user might have read access but not be a "member")
            accessible_channels = channels[:10]  # Limit to first 10 channels to avoid rate limits
            
            all_messages = []
            
            print(f"=== DEBUG: Fetching messages from {len(accessible_channels)} channels ===")
            for channel in accessible_channels:
                try:
                    print(f"Fetching messages from #{channel['name']} (is_member: {channel.get('is_member')})")
                    response = httpx.get(
                        'https://slack.com/api/conversations.history',
                        headers={'Authorization': f'Bearer {access_token}'},
                        params={
                            'channel': channel['id'],
                            'oldest': today_timestamp,
                            'limit': 20
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get('ok'):
                        messages = data.get('messages', [])
                        print(f"  -> Found {len(messages)} messages in #{channel['name']}")
                        for message in messages:
                            # Skip messages from bots unless they mention the user
                            if message.get('subtype') == 'bot_message':
                                continue
                                
                            message_data = {
                                'channel_id': channel['id'],
                                'channel_name': channel['name'],
                                'timestamp': message.get('ts'),
                                'user': message.get('user'),
                                'text': message.get('text', ''),
                                'thread_ts': message.get('thread_ts'),
                                'reply_count': message.get('reply_count', 0),
                                'is_thread_reply': message.get('thread_ts') and message.get('thread_ts') != message.get('ts')
                            }
                            all_messages.append(message_data)
                    else:
                        print(f"  -> API Error for #{channel['name']}: {data.get('error', 'Unknown error')}")
                            
                except Exception as e:
                    print(f"  -> Exception fetching messages from #{channel['name']}: {str(e)}")
                    continue
            
            # Sort by timestamp (most recent first)
            all_messages.sort(key=lambda x: float(x.get('timestamp', 0)), reverse=True)
            
            return all_messages[:limit]
            
        except Exception as e:
            raise ValueError(f"Failed to fetch messages: {str(e)}")
    
    def get_mentions_today(self) -> List[Dict[str, Any]]:
        """Get messages that mention the authenticated user from today"""
        access_token = self.get_valid_credentials()
        if not access_token:
            raise ValueError("Not authenticated with Slack")
        
        # Get user info to find user ID
        user_info = self.get_connection_info().get('user_info', {})
        user_id = user_info.get('user_id')
        if not user_id:
            raise ValueError("Could not determine user ID")
        
        try:
            # Search for mentions of the user today
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_str = today.strftime('%Y-%m-%d')
            
            response = httpx.get(
                'https://slack.com/api/search.messages',
                headers={'Authorization': f'Bearer {access_token}'},
                params={
                    'query': f'<@{user_id}> after:{today_str}',
                    'count': 20
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('ok'):
                raise ValueError(f"Slack API error: {data.get('error', 'Unknown error')}")
            
            mentions = []
            for match in data.get('messages', {}).get('matches', []):
                mentions.append({
                    'channel_id': match.get('channel', {}).get('id'),
                    'channel_name': match.get('channel', {}).get('name'),
                    'timestamp': match.get('ts'),
                    'user': match.get('user'),
                    'text': match.get('text', ''),
                    'permalink': match.get('permalink')
                })
            
            return mentions
            
        except Exception as e:
            # If search fails, fallback to checking recent messages for mentions
            print(f"Mention search failed, using fallback: {str(e)}")
            return self._get_mentions_fallback(user_id)
    
    def _get_mentions_fallback(self, user_id: str) -> List[Dict[str, Any]]:
        """Fallback method to find mentions by checking recent messages"""
        try:
            messages = self.get_messages_today(100)
            mentions = []
            
            for message in messages:
                if f'<@{user_id}>' in message.get('text', ''):
                    mentions.append(message)
            
            return mentions
            
        except Exception as e:
            print(f"Fallback mention search failed: {str(e)}")
            return []
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()