# Gmail OAuth 2.0 Implementation for ZeroTask

## Overview

This document describes the complete Gmail OAuth 2.0 Desktop flow implementation for ZeroTask, following PRD Section 8 specifications. The implementation provides secure, local-first Gmail integration for the daily brief system.

## Architecture Components

### 1. Database Models (`app/models/tokens.py`)

#### OAuthToken Model
- **Purpose**: Store encrypted OAuth tokens with refresh capability
- **Fields**:
  - `encrypted_access_token`: AES-256 encrypted Gmail access token
  - `encrypted_refresh_token`: AES-256 encrypted refresh token
  - `expires_at`: Token expiration timestamp for automatic refresh
  - `scope`: Granted OAuth scopes verification
  - `is_active`: Token validity status

### 2. Gmail OAuth Service (`app/services/gmail_oauth_service.py`)

#### Key Features
- **Desktop OAuth Flow**: Implements Google's Desktop OAuth 2.0 pattern
- **Secure Token Management**: AES-256 encryption for token storage
- **Automatic Token Refresh**: Handles token expiration transparently
- **CSRF Protection**: Uses secure state parameters
- **Error Handling**: Comprehensive error handling with user-friendly messages

#### Core Methods
- `generate_auth_url()`: Creates OAuth authorization URL with state
- `exchange_code_for_tokens()`: Exchanges authorization code for tokens
- `get_valid_credentials()`: Returns valid credentials, refreshing if needed
- `revoke_access()`: Revokes tokens and cleans up stored data

### 3. Gmail API Service (`app/services/gmail_api_service.py`)

#### Email Operations
- **Read Recent Messages**: Fetch emails with filtering and pagination
- **Today's Messages**: Get today's emails for daily brief
- **Important Threads**: Identify important email conversations
- **Thread Details**: Full thread context with all messages

#### Draft Management
- **Create Draft Replies**: Generate draft responses (no auto-send)
- **Thread Preservation**: Maintains email thread context
- **Reply Headers**: Proper In-Reply-To and References headers

### 4. API Endpoints

#### Authentication Endpoints (`app/api/auth.py`)
- `GET /api/v1/auth/gmail/status` - OAuth connection status
- `GET /api/v1/auth/gmail/oauth/start` - Start OAuth flow
- `GET /oauth2/callback` - Handle OAuth callback
- `POST /api/v1/auth/gmail/oauth/revoke` - Revoke access
- `GET /api/v1/auth/gmail/test` - Test API connection

#### Gmail API Endpoints (`app/api/gmail.py`)
- `GET /api/v1/gmail/profile` - User profile and account info
- `GET /api/v1/gmail/emails/recent` - Recent emails with filtering
- `GET /api/v1/gmail/emails/today` - Today's emails for daily brief
- `GET /api/v1/gmail/threads/important` - Important email threads
- `POST /api/v1/gmail/drafts/reply` - Create draft reply
- `POST /api/v1/gmail/search` - Search emails with Gmail query syntax
- `GET /api/v1/gmail/labels` - Get Gmail labels for filtering

## Security Architecture

### OAuth 2.0 Security Measures

#### 1. Desktop OAuth Flow
- **Redirect URI**: `http://localhost:8000/oauth2/callback` (no public URLs)
- **Client Type**: Desktop application (no client secret exposure)
- **PKCE**: Implicit through Google's desktop flow implementation
- **State Parameter**: CSRF protection with secure random tokens

#### 2. Token Security
- **Encryption**: All tokens encrypted with AES-256 before database storage
- **Key Management**: Uses application secret key for encryption
- **Rotation**: Automatic token refresh before expiration
- **Revocation**: Proper token revocation with Google and cleanup

#### 3. Scope Minimization
- **Read-Only Access**: `gmail.readonly` for email reading
- **Draft-Only Composition**: `gmail.compose` for drafts (no sending)
- **No Deletion**: No destructive operations on user's Gmail

### Local-First Security

#### 1. Data Handling
- **No External Transmission**: Email content processed locally only
- **Minimal Storage**: Only metadata and evidence links stored
- **User Control**: Complete user control over data and connections

#### 2. Network Security
- **HTTPS Only**: All Google API calls use HTTPS
- **Certificate Validation**: Proper SSL certificate validation
- **Rate Limiting**: Respects Gmail API rate limits

## Integration with Existing Architecture

### 1. Shared Service Account Pattern
- **IT Configuration**: OAuth credentials managed by IT team
- **Environment Variables**: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- **Consistent Patterns**: Follows same patterns as Slack/GitHub integration

### 2. Database Integration
- **SQLAlchemy Models**: Consistent with existing token storage patterns
- **Migration Support**: Automatic table creation through existing mechanism
- **Encryption Consistency**: Uses same encryption utilities as other services

### 3. API Consistency
- **FastAPI Patterns**: Consistent error handling and response formats
- **Pydantic Schemas**: Type-safe request/response validation
- **CORS Support**: Proper CORS configuration for frontend integration

## Frontend Integration

### 1. OAuth Flow UX
- **Popup Window**: OAuth flow opens in popup for better UX
- **Callback Handling**: Automatic callback processing with status display
- **Error Feedback**: Clear error messages for OAuth failures
- **Status Updates**: Real-time status updates after OAuth completion

### 2. Connection Management
- **Connect/Disconnect**: Easy connection management UI
- **Status Display**: Clear connection status indicators
- **Test Functionality**: Test API connection capability
- **IT Setup Info**: Clear instructions for IT team setup

## Daily Brief Integration

### 1. Email Data Sources
```python
# Today's emails for daily brief
today_emails = await GmailApiService.get_today_messages(db, max_results=50)

# Important ongoing threads
important_threads = await GmailApiService.get_important_threads(db, days_back=7)

# Specific searches
search_results = await GmailApiService.search_emails(db, "is:unread from:team@company.com")
```

### 2. Evidence Links
- **Gmail Web Links**: Direct links to emails in Gmail web interface
- **Thread Context**: Links to specific messages within threads
- **Search Results**: Links to Gmail search results for queries

### 3. Action Integration
```python
# Create draft reply from daily brief card
draft_result = await GmailApiService.create_draft_reply(
    db=db,
    message_id="email_id_from_brief",
    draft_content="LLM-generated response",
    subject_prefix="Re: "
)
```

## Configuration and Deployment

### 1. IT Team Setup
1. **Google Cloud Console Setup**:
   - Create Google Cloud Project
   - Enable Gmail API
   - Create OAuth 2.0 Desktop Application credentials
   - Configure redirect URI: `http://localhost:8000/oauth2/callback`

2. **Environment Configuration**:
   ```bash
   GOOGLE_CLIENT_ID=your_oauth_client_id
   GOOGLE_CLIENT_SECRET=your_oauth_client_secret
   ```

3. **Scope Verification**:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.compose`

### 2. User Setup Process
1. Navigate to Sources page in ZeroTask frontend
2. Click "Connect Gmail" button
3. Complete OAuth flow in popup window
4. Verify connection with "Test API" button
5. Gmail integration ready for daily brief

### 3. Error Recovery
- **Token Expiration**: Automatic refresh handles most cases
- **Connection Issues**: Clear error messages with retry options
- **OAuth Failures**: Detailed error information with recovery steps
- **Revocation**: Clean disconnect and re-authentication capability

## API Usage Examples

### 1. Authentication Check
```bash
curl -X GET "http://localhost:8000/api/v1/auth/gmail/status"
```

### 2. Start OAuth Flow
```bash
curl -X GET "http://localhost:8000/api/v1/auth/gmail/oauth/start"
```

### 3. Get Today's Emails
```bash
curl -X GET "http://localhost:8000/api/v1/gmail/emails/today?max_results=20"
```

### 4. Create Draft Reply
```bash
curl -X POST "http://localhost:8000/api/v1/gmail/drafts/reply" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "email_message_id",
    "content": "Thank you for your email. I will review and respond shortly.",
    "subject_prefix": "Re: "
  }'
```

### 5. Search Emails
```bash
curl -X POST "http://localhost:8000/api/v1/gmail/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "is:unread after:2024/01/01",
    "max_results": 25
  }'
```

## Error Handling and Monitoring

### 1. Common Error Scenarios
- **OAuth Not Configured**: Clear message directing to IT team
- **Authentication Required**: Instructions to complete OAuth flow
- **Token Expired**: Automatic refresh attempt with fallback
- **API Rate Limits**: Proper backoff and retry logic
- **Network Issues**: Graceful degradation with offline indication

### 2. Logging and Monitoring
- **OAuth Events**: Successful/failed authentication attempts
- **API Usage**: Request counts and error rates
- **Token Management**: Refresh events and expiration handling
- **Performance**: API response times and success rates

## Compliance and Privacy

### 1. Data Privacy
- **Local Processing**: All email content processed locally
- **Minimal Storage**: Only metadata and links stored persistently
- **User Consent**: Explicit OAuth consent for each scope
- **Data Retention**: User controls data through revocation

### 2. Security Compliance
- **Encryption Standards**: AES-256 for stored tokens
- **Access Controls**: User-specific token isolation
- **Audit Trail**: OAuth events and access logging
- **Secure Defaults**: Secure-by-default configuration

This implementation provides a robust, secure, and user-friendly Gmail integration that follows OAuth 2.0 best practices while maintaining ZeroTask's local-first architecture principles.