"""Configuration management using Pydantic BaseSettings."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Telegram API settings
    api_id: int = Field(..., alias="API_ID", description="Telegram API ID")
    api_hash: str = Field(..., alias="API_HASH", description="Telegram API Hash")
    phone: str = Field(..., alias="PHONE", description="Phone number for Telegram")
    channel: str = Field(..., alias="CHANNEL", description="Target channel/group")
    
    # Optional bot token for future features
    tg_bot_token: Optional[str] = Field(None, alias="TG_BOT_TOKEN", description="Telegram Bot Token")
    
    # Sentry configuration
    sentry_dsn: Optional[str] = Field(None, alias="SENTRY_DSN", description="Sentry DSN for error tracking")
    
    # Session file path
    session_name: str = Field("premium_user_session", alias="SESSION_NAME", description="Telethon session file name")
    
    # Admin log chat ID
    admin_log_chat: Optional[str] = Field(None, alias="ADMIN_LOG_CHAT", description="Chat ID for admin logging")
    
    # Bot token for posting
    bot_token: Optional[str] = Field(None, alias="TG_BOT_TOKEN", description="Telegram bot token for posting")


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings() 