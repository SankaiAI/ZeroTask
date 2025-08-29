from app.config import settings

class SharedAuthService:
    """Shared authentication service for IT-managed service accounts - PRD Section 8 & 10"""
    
    @staticmethod
    def is_github_configured() -> bool:
        """Check if GitHub service account token is configured"""
        return bool(settings.github_token.strip())
    
    @staticmethod
    def is_slack_configured() -> bool:
        """Check if Slack app tokens are configured"""
        return bool(settings.slack_app_token.strip() and settings.slack_bot_token.strip())
    
    @staticmethod
    def is_gmail_configured() -> bool:
        """Check if Gmail OAuth credentials are configured"""
        return bool(settings.google_client_id.strip() and settings.google_client_secret.strip())
    
    @staticmethod
    def get_github_token() -> str:
        """Get GitHub service account token"""
        if not SharedAuthService.is_github_configured():
            raise ValueError("GitHub service account token not configured by IT team")
        return settings.github_token
    
    @staticmethod
    def get_slack_tokens() -> tuple[str, str]:
        """Get Slack app and bot tokens"""
        if not SharedAuthService.is_slack_configured():
            raise ValueError("Slack tokens not configured by IT team")
        return settings.slack_app_token, settings.slack_bot_token
    
    @staticmethod
    def get_gmail_credentials() -> tuple[str, str]:
        """Get Gmail OAuth credentials"""
        if not SharedAuthService.is_gmail_configured():
            raise ValueError("Gmail OAuth credentials not configured by IT team")
        return settings.google_client_id, settings.google_client_secret
    
    @staticmethod
    def get_connection_status() -> dict:
        """Get status of all configured connections"""
        return {
            "github": {
                "configured": SharedAuthService.is_github_configured(),
                "status": "IT Configured" if SharedAuthService.is_github_configured() else "Not Configured"
            },
            "slack": {
                "configured": SharedAuthService.is_slack_configured(),
                "status": "IT Configured" if SharedAuthService.is_slack_configured() else "Not Configured"
            },
            "gmail": {
                "configured": SharedAuthService.is_gmail_configured(),
                "status": "IT Configured" if SharedAuthService.is_gmail_configured() else "Not Configured"
            }
        }
    
    @staticmethod
    def validate_all_connections() -> dict:
        """Validate all service account connections on startup"""
        status = SharedAuthService.get_connection_status()
        
        configured_count = sum(1 for service in status.values() if service["configured"])
        total_count = len(status)
        
        return {
            "configured_services": configured_count,
            "total_services": total_count,
            "all_configured": configured_count == total_count,
            "services": status
        }