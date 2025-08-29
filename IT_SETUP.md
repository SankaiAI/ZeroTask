# ZeroTask IT Setup Guide

## Overview
ZeroTask uses shared service accounts for company-wide deployment, eliminating the need for individual users to manage API tokens. This guide helps IT teams set up the required service accounts and credentials.

## Prerequisites
- Company Slack workspace admin access
- GitHub organization admin access
- Ability to create service accounts and manage tokens

## 🔧 GitHub Service Account Setup

### 1. Create Service Account
```bash
# Create a dedicated service account email
# Example: zerotask-bot@yourcompany.com
```

### 2. GitHub Organization Setup
1. **Create GitHub user account** for `zerotask-bot@yourcompany.com`
2. **Invite to GitHub organization** with appropriate team membership
3. **Grant repository access** to relevant repositories that need monitoring
4. **Generate Personal Access Token**:
   - Go to Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Name: "ZeroTask Company Integration"
   - Expiration: 90 days (set calendar reminder for renewal)
   - Scopes:
     - `repo` - Full repository access
     - `read:user` - Read user profile information
     - `notifications` - Access notifications
5. **Save token securely** - you'll need it for ZeroTask configuration

### 3. Repository Permissions
Ensure the service account has read access to:
- All repositories where team members have assigned issues/PRs
- Repositories where PR reviews are requested from team members

## 💬 Slack App Setup

### 1. Create Company Slack App
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. App Name: `ZeroTask`
4. Choose your company workspace

### 2. Enable Socket Mode
1. Go to **Settings → Socket Mode**
2. Toggle **"Enable Socket Mode"** ✅
3. Click **"Generate App-Level Token"**
4. Token Name: `ZeroTask Connection`
5. Scope: `connections:write`
6. **Save the App Token** (starts with `xapp-`)

### 3. Configure OAuth Scopes
1. Go to **Features → OAuth & Permissions**
2. Add **Bot Token Scopes**:
   - `app_mentions:read` - Read messages that mention the app
   - `channels:history` - Read messages in channels
   - `chat:write` - Send messages
   - `im:history` - Read direct messages
   - `channels:read` - List channels
   - `users:read` - Read user information

### 4. Install to Workspace
1. Click **"Install to Workspace"**
2. Review permissions and click **"Allow"**
3. **Save the Bot User OAuth Token** (starts with `xoxb-`)

### 5. Channel Access (Optional)
- Add the ZeroTask bot to relevant channels where team discussions happen
- The bot will only read messages where it's mentioned or in channels it's added to

## 📧 Gmail Setup (Future Implementation)
Gmail integration will use company OAuth application:
1. Create Google Cloud Project for your organization
2. Enable Gmail API
3. Configure OAuth 2.0 credentials for desktop application
4. Set redirect URI to `http://localhost:8000/oauth2/callback`

## 🔐 ZeroTask Configuration

### Environment Variables
Update ZeroTask deployment with the obtained credentials:

```bash
# .env file or deployment configuration
GITHUB_TOKEN=ghp_your_github_service_account_token
SLACK_APP_TOKEN=xapp-your_app_token
SLACK_BOT_TOKEN=xoxb-your_bot_token

# Optional: Gmail (when implemented)
GOOGLE_CLIENT_ID=your_oauth_client_id
GOOGLE_CLIENT_SECRET=your_oauth_client_secret
```

### Deployment Notes
- Tokens should be stored securely in your deployment system
- Consider using secret management tools (HashiCorp Vault, AWS Secrets Manager, etc.)
- Set up monitoring for token expiration dates
- Implement token rotation procedures

## 🔄 Maintenance

### Token Rotation Schedule
- **GitHub PAT**: Rotate every 90 days
- **Slack Tokens**: Monitor for revocation, rotate annually or as needed
- **Calendar Reminders**: Set reminders 1 week before expiration

### Monitoring
- Monitor API rate limits for both GitHub and Slack
- Set up alerts for authentication failures
- Regular access reviews for service account permissions

### User Support
- Users should not need individual tokens
- Direct users to IT team for any authentication issues
- Provide users with list of available channels/repositories

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] GitHub service account created and configured
- [ ] Slack app created with proper scopes
- [ ] Tokens stored securely in deployment system
- [ ] Rate limiting and monitoring configured

### Post-Deployment
- [ ] Test GitHub integration with sample repositories
- [ ] Test Slack integration with sample channels
- [ ] Verify users can see available sources without entering tokens
- [ ] Set up token expiration monitoring

### User Communication
- [ ] Notify team that ZeroTask is available
- [ ] Share list of monitored repositories and channels
- [ ] Provide support contact for IT team

## 🆘 Troubleshooting

### Common Issues
1. **"GitHub authentication failed"**
   - Check service account repository access
   - Verify PAT hasn't expired
   - Ensure all required scopes are selected

2. **"Slack connection issues"**
   - Verify Socket Mode is enabled
   - Check bot is added to relevant channels
   - Confirm app-level token has `connections:write` scope

3. **"No data in daily brief"**
   - Verify service accounts have access to relevant resources
   - Check that users have configured which channels/repos to monitor
   - Review API rate limiting logs

---

For questions or issues, contact the IT team or ZeroTask administrators.