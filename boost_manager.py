import asyncio
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl import functions

load_dotenv()

console = Console()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
CHANNEL = os.getenv("CHANNEL")

client = TelegramClient("premium_user_session", API_ID, API_HASH)


async def apply_boost(slots: int = 1):
    try:
        await client.start(phone=PHONE)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking boost slots...", total=None)

            try:
                channel_entity = await client.get_entity(CHANNEL)

                # Check available boost slots first
                progress.update(task, description="Checking available slots...")
                my_boosts = await client(functions.premium.GetMyBoostsRequest())

                if hasattr(my_boosts, "available_slots"):
                    available = my_boosts.available_slots
                else:
                    available = 4  # Default assumption

                console.print(f"📊 Available boost slots: {available}")

                if available < slots:
                    console.print(
                        Panel(
                            f"⚠️ Not enough boost slots available!\n"
                            f"Requested: {slots}, Available: {available}",
                            title="Insufficient Slots",
                            border_style="yellow",
                        )
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
                    else:
                        console.print(f"✅ Boost #{i+1} applied successfully!")

            except FloodWaitError as e:
                console.print(
                    Panel(
                        f"⏳ Flood wait detected. Waiting {e.seconds} seconds...",
                        title="Rate Limit",
                        border_style="yellow",
                    )
                )
                await asyncio.sleep(e.seconds)
                return await apply_boost(slots)

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
    finally:
        await client.disconnect()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Telegram Channel Boost Manager")
    parser.add_argument(
        "--slots",
        type=int,
        default=1,
        help="Number of boost slots to apply (default: 1)",
    )
    args = parser.parse_args()

    asyncio.run(apply_boost(args.slots))
