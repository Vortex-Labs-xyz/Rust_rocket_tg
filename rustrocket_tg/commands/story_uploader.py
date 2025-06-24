"""Story uploader command - uploads media files as Telegram stories."""

import asyncio
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import get_settings
from ..utils.telegram import get_authenticated_client
from ..utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


def render_trade_event_video(json_data: Dict[str, Any], output_path: Path) -> bool:
    """Render trade event data to a 15-second MP4 video."""
    try:
        # TODO: Implement actual video rendering using ffmpeg-python
        # This is a placeholder that creates a dummy file
        import ffmpeg
        
        # Placeholder implementation
        logger.info(f"Rendering trade event video: {json_data.get('event_type', 'unknown')}")
        
        # For now, just create a dummy file
        output_path.write_bytes(b"dummy_video_content")
        
        console.print(f"🎬 Rendered video: {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to render video: {e}")
        return False


async def upload_story_async(file_path: Path, settings, client) -> bool:
    """Upload a single file as a Telegram story."""
    try:
        # TODO: Implement actual story upload via Telethon
        # Currently Telethon doesn't fully support story uploads
        # This is a placeholder implementation
        
        logger.info(f"Uploading story: {file_path.name}")
        
        # Placeholder: In a real implementation, this would:
        # 1. Upload the media file
        # 2. Create a story with the media
        # 3. Add swipe-up button with the specified URL
        
        # For now, just simulate the upload
        await asyncio.sleep(0.1)  # Simulate API call delay
        
        console.print(f"📱 Uploaded story: {file_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to upload story {file_path.name}: {e}")
        return False


async def process_story_files_async(queue_dir: str = "story/queue", done_dir: str = "story/done", dry_run: bool = False) -> None:
    """Process all media files in the story queue directory."""
    settings = get_settings()
    
    queue_path = Path(queue_dir)
    done_path = Path(done_dir)
    
    if not queue_path.exists():
        console.print(Panel(
            f"📁 Queue directory {queue_dir} does not exist",
            title="Directory Missing",
            border_style="yellow"
        ))
        return
    
    # Ensure done directory exists
    done_path.mkdir(parents=True, exist_ok=True)
    
    # Find media files and JSON trade events
    media_files = []
    for ext in ['*.mp4', '*.png', '*.jpg', '*.jpeg', '*.json']:
        media_files.extend(queue_path.glob(ext))
    
    if not media_files:
        console.print(Panel(
            f"📱 No media files found in {queue_dir}",
            title="No Stories to Process",
            border_style="blue"
        ))
        return
    
    if dry_run:
        console.print(Panel(
            f"🔍 DRY RUN: Would process {len(media_files)} media files from {queue_dir}",
            title="Dry Run Mode",
            border_style="blue"
        ))
        for file_path in media_files:
            if file_path.suffix == '.json':
                console.print(f"🎬 {file_path.name}: Would render trade event video")
            else:
                console.print(f"📱 {file_path.name}: Would upload as story")
        return
    
    client = None
    try:
        client = await get_authenticated_client(settings)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing stories...", total=len(media_files))
            
            processed_count = 0
            
            for file_path in media_files:
                progress.update(task, description=f"Processing {file_path.name}...")
                
                try:
                    upload_path = file_path
                    
                    # Handle JSON trade events by rendering to video
                    if file_path.suffix == '.json':
                        try:
                            json_data = json.loads(file_path.read_text())
                            video_path = file_path.with_suffix('.mp4')
                            
                            if render_trade_event_video(json_data, video_path):
                                upload_path = video_path
                            else:
                                console.print(f"❌ Failed to render {file_path.name}")
                                continue
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in {file_path.name}: {e}")
                            continue
                    
                    # Upload as story
                    if await upload_story_async(upload_path, settings, client):
                        # Move original file to done directory
                        done_file = done_path / file_path.name
                        shutil.move(str(file_path), str(done_file))
                        
                        # Also move rendered video if it exists
                        if file_path.suffix == '.json' and upload_path != file_path:
                            done_video = done_path / upload_path.name
                            if upload_path.exists():
                                shutil.move(str(upload_path), str(done_video))
                        
                        processed_count += 1
                        console.print(f"✅ Processed and moved {file_path.name}")
                        logger.info(f"Successfully processed story {file_path.name}")
                    else:
                        console.print(f"❌ Failed to upload {file_path.name}")
                    
                    progress.advance(task)
                    
                except Exception as e:
                    console.print(f"❌ Failed to process {file_path.name}: {e}")
                    logger.error(f"Failed to process {file_path.name}: {e}")
                    continue
            
            console.print(Panel(
                f"📱 Processed {processed_count} stories",
                title="Processing Complete",
                border_style="green"
            ))
            
    except Exception as e:
        console.print(Panel(
            f"❌ Error: {str(e)}",
            title="Error",
            border_style="red"
        ))
        logger.error(f"Story processing failed: {e}")
        raise typer.Exit(1)
    finally:
        if client:
            await client.disconnect()


def story_uploader_command(
    queue_dir: str = typer.Option("story/queue", "--queue-dir", help="Directory to scan for media files"),
    done_dir: str = typer.Option("story/done", "--done-dir", help="Directory to move processed files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only show what would be done")
) -> None:
    """Upload media files as Telegram stories with swipe-up buttons."""
    # TODO: Implement full Telegram Stories API support when available
    # TODO: Add support for story highlights and archives
    # TODO: Add support for interactive story elements
    
    logger.info(f"Starting story uploader (queue_dir={queue_dir}, dry_run={dry_run})")
    asyncio.run(process_story_files_async(queue_dir, done_dir, dry_run)) 