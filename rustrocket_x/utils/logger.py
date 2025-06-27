"""Rich logger setup with optional Sentry integration."""

import logging
from typing import Optional

import sentry_sdk
from rich.console import Console
from rich.logging import RichHandler

from ..config import Settings

console = Console()


def setup_logging(settings: Settings, level: str = "INFO") -> logging.Logger:
    """Setup logging with Rich handler and optional Sentry."""

    # Setup Sentry if DSN is provided
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=1.0,
        )

    # Create logger
    logger = logging.getLogger("rustrocket_x")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add rich handler
    rich_handler = RichHandler(
        console=console, show_time=True, show_path=False, markup=True
    )
    rich_handler.setFormatter(logging.Formatter(fmt="%(message)s", datefmt="[%X]"))

    logger.addHandler(rich_handler)
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name or "rustrocket_x")
