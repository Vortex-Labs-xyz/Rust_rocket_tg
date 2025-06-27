import asyncio
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from telethon import TelegramClient
from telethon.tl import functions

load_dotenv()

console = Console()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
CHANNEL = os.getenv("CHANNEL")

client = TelegramClient("premium_user_session", API_ID, API_HASH)


async def check_expiring_boosts():
    try:
        await client.start(phone=PHONE)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking boost expiration times...", total=None)

            channel_entity = await client.get_entity(CHANNEL)

            result = await client(
                functions.premium.GetBoostsListRequest(
                    peer=channel_entity, offset="", limit=100
                )
            )

            progress.update(task, description="Sending reminders...")

            three_days_seconds = 3 * 24 * 60 * 60
            reminders_sent = 0

            for boost in result.boosts:
                if hasattr(boost, "expires") and boost.expires:
                    expires_in_seconds = boost.expires

                    if expires_in_seconds < three_days_seconds:
                        try:
                            user_entity = await client.get_entity(boost.user_id)

                            days_left = expires_in_seconds // (24 * 60 * 60)
                            hours_left = (expires_in_seconds % (24 * 60 * 60)) // 3600

                            message = (
                                f"🚨 Dein Boost läuft bald aus!\n\n"
                                f"⏰ Verbleibende Zeit: {days_left} Tage, {hours_left} Stunden\n"
                                f"📢 Channel: {CHANNEL}\n\n"
                                f"💎 Erneuere deinen Boost, um den Channel weiter zu unterstützen!"
                            )

                            await client.send_message(user_entity, message)
                            reminders_sent += 1

                            console.print(f"✅ Reminder sent to user {boost.user_id}")

                        except Exception as e:
                            console.print(
                                f"⚠️ Could not send reminder to user {boost.user_id}: {e}"
                            )

            console.print(
                Panel(
                    f"📨 Reminders sent: {reminders_sent}\n"
                    f"📊 Total boosts checked: {len(result.boosts)}",
                    title="Reminder Summary",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(check_expiring_boosts())
