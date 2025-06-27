"""Boost manager command - applies boosts to Telegram channels."""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from telethon import TelegramClient
from telethon.tl import functions
from telethon.errors import FloodWaitError

from ..config import get_settings
from ..utils.telegram import get_authenticated_client
from ..utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


async def apply_boost_async(slots: int = 1, dry_run: bool = False) -> None:
    """Apply boost to the configured channel/group."""
    settings = get_settings()

    if dry_run:
        console.print(
            Panel(
                f"🔍 DRY RUN: Would apply {slots} boost(s) to {settings.channel}",
                title="Dry Run Mode",
                border_style="blue",
            )
        )
        return

    client = None
    try:
        client = await get_authenticated_client(settings)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking boost slots...", total=None)

            try:
                channel_entity = await client.get_entity(settings.channel)

                # Check available boost slots first
                progress.update(task, description="Checking available slots...")
                my_boosts = await client(functions.premium.GetMyBoostsRequest())

                if hasattr(my_boosts, "available_slots"):
                    available = my_boosts.available_slots
                else:
                    available = 4  # Default assumption

                console.print(f"📊 Available boost slots: {available}")
                logger.info(f"Available boost slots: {available}")

                if available < slots:
                    console.print(
                        Panel(
                            f"⚠️ Not enough boost slots available!\n"
                            f"Requested: {slots}, Available: {available}",
                            title="Insufficient Slots",
                            border_style="yellow",
                        )
                    )
                    logger.warning(
                        f"Not enough slots: requested {slots}, available {available}"
                    )
                    return

                progress.update(task, description="Applying boost...")

                for i in range(slots):
                    result = await client(
                        functions.premium.ApplyBoostRequest(peer=channel_entity)
                    )

                    if hasattr(result, "level") and hasattr(
                        result, "current_level_boosts"
                    ):
                        level = result.level
                        progress_boosts = result.current_level_boosts

                        console.print(
                            Panel(
                                f"✅ Boost #{i+1} applied successfully!\n"
                                f"📊 Channel Level: {level}\n"
                                f"🚀 Current Boosts: {progress_boosts}",
                                title="Boost Status",
                                border_style="green",
                            )
                        )
                        logger.info(
                            f"Boost #{i+1} applied successfully - Level: {level}, Boosts: {progress_boosts}"
                        )
                    else:
                        console.print(f"✅ Boost #{i+1} applied successfully!")
                        logger.info(f"Boost #{i+1} applied successfully")

            except FloodWaitError as e:
                console.print(
                    Panel(
                        f"⏳ Flood wait detected. Waiting {e.seconds} seconds...",
                        title="Rate Limit",
                        border_style="yellow",
                    )
                )
                logger.warning(f"Flood wait: {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
                return await apply_boost_async(slots, dry_run)

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
        logger.error(f"Boost application failed: {e}")
        raise typer.Exit(1)
    finally:
        if client:
            await client.disconnect()


def boost_manager_command(
    slots: int = typer.Option(
        1, "--slots", "-s", help="Number of boost slots to apply"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Only show what would be done"
    ),
) -> None:
    """Apply boosts to the configured Telegram channel."""
    # TODO: Add validation for slots parameter
    # TODO: Add support for scheduling boosts
    # TODO: Add support for multiple channels

    logger.info(f"Starting boost manager with {slots} slots (dry_run={dry_run})")
    asyncio.run(apply_boost_async(slots, dry_run))
