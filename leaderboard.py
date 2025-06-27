import asyncio
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from telethon import TelegramClient
from telethon.tl import functions

load_dotenv()

console = Console()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
CHANNEL = os.getenv("CHANNEL")

client = TelegramClient("premium_user_session", API_ID, API_HASH)


async def show_leaderboard():
    try:
        await client.start(phone=PHONE)

        channel_entity = await client.get_entity(CHANNEL)

        result = await client(
            functions.premium.GetBoostsListRequest(
                peer=channel_entity, offset="", limit=10
            )
        )

        table = Table(title="🏆 Top 10 Boosters")
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("User ID", style="magenta")
        table.add_column("Boosts", style="green", justify="right")
        table.add_column("Expires (min)", style="yellow", justify="right")

        for i, boost in enumerate(result.boosts[:10], 1):
            if hasattr(boost, "expires") and boost.expires:
                import datetime

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

        if hasattr(result, "count"):
            console.print(
                Panel(
                    f"📊 Total Boosters: {result.count}",
                    title="Statistics",
                    border_style="blue",
                )
            )

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(show_leaderboard())
