import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="sqlite:///./zerotask.db")
    
    # API Configuration
    api_host: str = Field(default="localhost")
    api_port: int = Field(default=8000)
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:3001"])
    
    # LLM Configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama2")
    
    # Polling Configuration
    slack_poll_interval: int = Field(default=5)  # minutes
    github_poll_interval: int = Field(default=5)  # minutes
    
    # Daily Brief Settings
    daily_brief_hour: int = Field(default=9)  # 9 AM
    
    # Security
    app_secret: str = Field(default="zerotask-local-secret-key")
    machine_id: str = Field(default="dev-machine-001")
    
    # Shared Service Account Credentials (IT-managed)
    github_token: str = Field(default="", description="GitHub service account PAT")
    slack_app_token: str = Field(default="", description="Slack app-level token (xapp-)")
    slack_bot_token: str = Field(default="", description="Slack bot user token (xoxb-)")
    google_client_id: str = Field(default="", description="Google OAuth client ID")
    google_client_secret: str = Field(default="", description="Google OAuth client secret")
    
    # Individual OAuth Credentials (User connections)
    slack_client_id: str = Field(default="", description="Slack OAuth client ID")
    slack_client_secret: str = Field(default="", description="Slack OAuth client secret")
    
    # Development
    debug: bool = Field(default=False)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()