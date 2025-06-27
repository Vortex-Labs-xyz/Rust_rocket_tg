"""Reminder command - sends DM reminders for expiring boosts."""

import asyncio
import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from telethon.tl import functions

from ..config import get_settings
from ..utils.telegram import get_authenticated_client
from ..utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


async def check_expiring_boosts_async(
    days_threshold: int = 3, dry_run: bool = False
) -> None:
    """Check for expiring boosts and send reminder messages."""
    settings = get_settings()

    if dry_run:
        console.print(
            Panel(
                f"🔍 DRY RUN: Would check for boosts expiring within {days_threshold} days for {settings.channel}",
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
            task = progress.add_task("Checking boost expiration times...", total=None)

            channel_entity = await client.get_entity(settings.channel)

            result = await client(
                functions.premium.GetBoostsListRequest(
                    peer=channel_entity, offset="", limit=100
                )
            )

            progress.update(task, description="Sending reminders...")

            threshold_seconds = days_threshold * 24 * 60 * 60
            reminders_sent = 0

            for boost in result.boosts:
                if hasattr(boost, "expires") and boost.expires:
                    try:
                        if isinstance(boost.expires, datetime.datetime):
                            now = (
                                datetime.datetime.now(boost.expires.tzinfo)
                                if boost.expires.tzinfo
                                else datetime.datetime.now()
                            )
                            expires_in_seconds = int(
                                (boost.expires - now).total_seconds()
                            )
                        else:
                            expires_in_seconds = boost.expires

                        if (
                            expires_in_seconds < threshold_seconds
                            and expires_in_seconds > 0
                        ):
                            try:
                                user_entity = await client.get_entity(boost.user_id)

                                days_left = expires_in_seconds // (24 * 60 * 60)
                                hours_left = (
                                    expires_in_seconds % (24 * 60 * 60)
                                ) // 3600

                                message = (
                                    f"🚨 Dein Boost läuft bald aus!\n\n"
                                    f"⏰ Verbleibende Zeit: {days_left} Tage, {hours_left} Stunden\n"
                                    f"📢 Channel: {settings.channel}\n\n"
                                    f"💎 Erneuere deinen Boost, um den Channel weiter zu unterstützen!"
                                )

                                if not dry_run:
                                    await client.send_message(user_entity, message)

                                reminders_sent += 1
                                console.print(
                                    f"✅ Reminder sent to user {boost.user_id}"
                                )
                                logger.info(f"Reminder sent to user {boost.user_id}")

                            except Exception as e:
                                console.print(
                                    f"⚠️ Could not send reminder to user {boost.user_id}: {e}"
                                )
                                logger.warning(
                                    f"Failed to send reminder to user {boost.user_id}: {e}"
                                )

                    except Exception as e:
                        logger.warning(f"Failed to process boost expiration: {e}")

            console.print(
                Panel(
                    f"📨 Reminders sent: {reminders_sent}\n"
                    f"📊 Total boosts checked: {len(result.boosts)}",
                    title="Reminder Summary",
                    border_style="green",
                )
            )
            logger.info(
                f"Reminder process completed: {reminders_sent} reminders sent, {len(result.boosts)} boosts checked"
            )

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
        logger.error(f"Reminder process failed: {e}")
        raise typer.Exit(1)
    finally:
        if client:
            await client.disconnect()


def reminder_command(
    days: int = typer.Option(
        3, "--days", "-d", help="Threshold in days for expiring boosts"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Only show what would be done"
    ),
) -> None:
    """Send reminder messages for boosts expiring within the specified threshold."""
    # TODO: Add support for custom reminder messages
    # TODO: Add support for scheduling reminder checks
    # TODO: Add support for different notification channels (email, webhook)

    logger.info(
        f"Starting reminder check with {days} days threshold (dry_run={dry_run})"
    )
    asyncio.run(check_expiring_boosts_async(days, dry_run))
