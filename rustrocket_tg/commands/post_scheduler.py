"""Post scheduler command - processes and publishes scheduled posts to Telegram."""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from telethon import Button, TelegramClient

from ..config import get_settings
from ..utils.logger import get_logger
from ..utils.telegram import get_authenticated_client

console = Console()
logger = get_logger(__name__)


def parse_markdown_file(file_path: Path) -> tuple[dict[str, Any], str]:
    """Parse markdown file with YAML front-matter."""
    content = file_path.read_text(encoding="utf-8")

    if content.startswith("---"):
        try:
            # Split front-matter and content
            parts = content.split("---", 2)
            if len(parts) >= 3:
                front_matter = yaml.safe_load(parts[1])
                markdown_content = parts[2].strip()
                return front_matter or {}, markdown_content
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML front-matter in {file_path}: {e}")

    return {}, content.strip()


def create_inline_keyboard(buttons: list[dict[str, str]]):
    """Create inline keyboard from button configuration for Telethon."""
    if not buttons:
        return None

    # Use Telethon's Button.url() helper
    keyboard_row = []
    for button in buttons:
        if "text" in button and "url" in button:
            keyboard_row.append(Button.url(button["text"], button["url"]))

    if keyboard_row:
        return [keyboard_row]  # Single row of buttons
    return None


async def process_post_files_async(
    queue_dir: str = "content/queue",
    done_dir: str = "content/done",
    dry_run: bool = False,
    use_bot: bool = False,
) -> None:
    """Process all markdown files in the queue directory."""
    settings = get_settings()

    queue_path = Path(queue_dir)
    done_path = Path(done_dir)

    if not queue_path.exists():
        console.print(
            Panel(
                f"📁 Queue directory {queue_dir} does not exist",
                title="Directory Missing",
                border_style="yellow",
            )
        )
        return

    # Ensure done directory exists
    done_path.mkdir(parents=True, exist_ok=True)

    md_files = list(queue_path.glob("*.md"))

    if not md_files:
        console.print(
            Panel(
                f"📝 No markdown files found in {queue_dir}",
                title="No Posts to Process",
                border_style="blue",
            )
        )
        return

    if dry_run:
        console.print(
            Panel(
                f"🔍 DRY RUN: Would process {len(md_files)} markdown files from {queue_dir}",
                title="Dry Run Mode",
                border_style="blue",
            )
        )
        for file_path in md_files:
            front_matter, content = parse_markdown_file(file_path)
            console.print(
                f"📄 {file_path.name}: pin={front_matter.get('pin', False)}, story={front_matter.get('story', False)}"
            )
        return

    client = None
    try:
        if use_bot and settings.bot_token:
            # Use bot client for posting (better for inline buttons)
            console.print("🤖 Using bot token for posting...")
            client = TelegramClient("bot_session", settings.api_id, settings.api_hash)
            await client.start(bot_token=settings.bot_token)
        else:
            # Use user client
            console.print("👤 Using user session for posting...")
            client = await get_authenticated_client(settings)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing posts...", total=len(md_files))

            channel_entity = await client.get_entity(settings.channel)

            for file_path in md_files:
                progress.update(task, description=f"Processing {file_path.name}...")

                try:
                    front_matter, content = parse_markdown_file(file_path)

                    # Create inline keyboard if buttons are specified
                    buttons_config = front_matter.get("buttons", [])
                    inline_buttons = create_inline_keyboard(buttons_config)

                    # Send message
                    # TODO: Add support for media attachments
                    message = await client.send_message(
                        channel_entity, content, buttons=inline_buttons
                    )

                    console.print(f"✔ Published {file_path.name}")
                    console.print(f"  Message ID: {message.id}")
                    logger.info(
                        f"Successfully sent message {message.id} from {file_path.name}"
                    )

                    # Pin message if requested
                    if front_matter.get("pin", False):
                        # TODO: Unpin previous pinned message first
                        await client.pin_message(channel_entity, message)
                        console.print("✔ Pinned")
                        console.print(f"  Chat ID: {message.chat_id}")
                        logger.info(
                            f"Pinned message {message.id} from {file_path.name}"
                        )

                    # Queue for story if requested
                    if front_matter.get("story", False):
                        # TODO: Add story content to story queue
                        story_queue_path = Path("story/queue")
                        story_queue_path.mkdir(parents=True, exist_ok=True)

                        story_data = {
                            "caption": content,
                            "buttons": buttons_config,
                            "source_post": file_path.name,
                        }

                        story_file = story_queue_path / f"{file_path.stem}_story.json"
                        story_file.write_text(yaml.dump(story_data), encoding="utf-8")
                        logger.info(f"Queued story content from {file_path.name}")

                    # Move to done directory
                    done_file = done_path / file_path.name
                    shutil.move(str(file_path), str(done_file))

                    logger.info(f"Successfully processed {file_path.name}")

                    progress.advance(task)

                except Exception as e:
                    console.print(f"❌ Failed to process {file_path.name}: {e}")
                    logger.error(f"Failed to process {file_path.name}: {e}")
                    continue

            console.print(
                Panel(
                    f"📨 Processed {len(md_files)} posts",
                    title="Processing Complete",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
        logger.error(f"Post processing failed: {e}")
        raise typer.Exit(1)
    finally:
        if client:
            await client.disconnect()


def post_scheduler_command(
    queue_dir: str = typer.Option(
        "content/queue", "--queue-dir", help="Directory to scan for markdown files"
    ),
    done_dir: str = typer.Option(
        "content/done", "--done-dir", help="Directory to move processed files"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Only show what would be done"
    ),
    use_bot: bool = typer.Option(
        False, "--use-bot", help="Use bot token instead of user session for posting"
    ),
) -> None:
    """Process and publish scheduled posts from markdown files with YAML front-matter."""
    # TODO: Add support for scheduling posts at specific times
    # TODO: Add support for media attachments (images, videos)
    # TODO: Add support for cross-posting to multiple channels

    logger.info(
        f"Starting post scheduler (queue_dir={queue_dir}, dry_run={dry_run}, use_bot={use_bot})"
    )
    asyncio.run(process_post_files_async(queue_dir, done_dir, dry_run, use_bot))
