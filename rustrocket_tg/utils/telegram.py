"""Telethon client factory and utilities."""

from telethon import TelegramClient
from ..config import Settings


def create_client(settings: Settings) -> TelegramClient:
    """Create and return a configured Telethon client."""
    return TelegramClient(
        settings.session_name,
        settings.api_id,
        settings.api_hash
    )


async def get_authenticated_client(settings: Settings) -> TelegramClient:
    """Get an authenticated Telethon client."""
    client = create_client(settings)
    await client.start(phone=settings.phone)
    return client 