"""Leaderboard command - shows top boosters for a Telegram channel."""

import asyncio
import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from telethon.tl import functions

from ..config import get_settings
from ..utils.logger import get_logger
from ..utils.telegram import get_authenticated_client

console = Console()
logger = get_logger(__name__)


async def show_leaderboard_async(limit: int = 10, dry_run: bool = False) -> None:
    """Show the top boosters leaderboard."""
    settings = get_settings()

    if dry_run:
        console.print(
            Panel(
                f"🔍 DRY RUN: Would show top {limit} boosters for {settings.channel}",
                title="Dry Run Mode",
                border_style="blue",
            )
        )
        return

    client = None
    try:
        client = await get_authenticated_client(settings)

        channel_entity = await client.get_entity(settings.channel)

        result = await client(
            functions.premium.GetBoostsListRequest(
                peer=channel_entity, offset="", limit=limit
            )
        )

        table = Table(title=f"🏆 Top {limit} Boosters")
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("User ID", style="magenta")
        table.add_column("Boosts", style="green", justify="right")
        table.add_column("Expires (min)", style="yellow", justify="right")

        for i, boost in enumerate(result.boosts[:limit], 1):
            if hasattr(boost, "expires") and boost.expires:
                try:
                    if isinstance(boost.expires, datetime.datetime):
                        now = (
                            datetime.datetime.now(boost.expires.tzinfo)
                            if boost.expires.tzinfo
                            else datetime.datetime.now()
                        )
                        expires_min = int((boost.expires - now).total_seconds() // 60)
                    else:
                        expires_min = boost.expires // 60
                except:
                    expires_min = "N/A"
            else:
                expires_min = "N/A"

            boosts_count = boost.multiplier if hasattr(boost, "multiplier") else 1
            user_id = boost.user_id if hasattr(boost, "user_id") else "Unknown"

            table.add_row(str(i), str(user_id), str(boosts_count), str(expires_min))

        console.print(table)
        logger.info(f"Displayed leaderboard with {len(result.boosts)} boosters")

        if hasattr(result, "count"):
            console.print(
                Panel(
                    f"📊 Total Boosters: {result.count}",
                    title="Statistics",
                    border_style="blue",
                )
            )
            logger.info(f"Total boosters: {result.count}")

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
        logger.error(f"Leaderboard display failed: {e}")
        raise typer.Exit(1)
    finally:
        if client:
            await client.disconnect()


def leaderboard_command(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of top boosters to show"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Only show what would be done"
    ),
) -> None:
    """Show the top boosters leaderboard for the configured channel."""
    # TODO: Add support for different sorting options
    # TODO: Add support for exporting leaderboard data
    # TODO: Add user name resolution instead of just IDs

    logger.info(f"Starting leaderboard display with limit {limit} (dry_run={dry_run})")
    asyncio.run(show_leaderboard_async(limit, dry_run))
