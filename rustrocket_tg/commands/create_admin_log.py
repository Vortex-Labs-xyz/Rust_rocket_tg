"""Create admin log command - creates a private mega-group for admin logging."""

import asyncio
import os
from pathlib import Path
from typing import Optional

import pyperclip
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from telethon import TelegramClient
from telethon.tl import functions, types
from telethon.tl.types import ChatAdminRights

from ..config import get_settings
from ..utils.telegram import get_authenticated_client
from ..utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


async def create_admin_log_group_async(group_name: str, write_env: bool = False) -> None:
    """Create a private mega-group for admin logging."""
    settings = get_settings()
    
    if not settings.tg_bot_token:
        console.print(Panel(
            "❌ TG_BOT_TOKEN is required in .env file to add bot as admin",
            title="Missing Bot Token",
            border_style="red"
        ))
        raise typer.Exit(1)
    
    client = None
    try:
        client = await get_authenticated_client(settings)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Step 1: Create the mega-group
            task = progress.add_task("Creating private mega-group...", total=4)
            
            try:
                # Create a mega-group (supergroup)
                result = await client(functions.channels.CreateChannelRequest(
                    title=group_name,
                    about=f"Private admin log group for {group_name}",
                    megagroup=True  # This creates a supergroup (mega-group)
                ))
                
                chat_id = result.chats[0].id
                # Convert to full chat ID format
                full_chat_id = -1000000000000 - chat_id
                
                console.print(f"✅ Created mega-group: {group_name}")
                logger.info(f"Created mega-group '{group_name}' with ID: {full_chat_id}")
                progress.advance(task)
                
                # Step 2: Get the bot entity
                progress.update(task, description="Finding bot...")
                
                # Extract bot username from token (first part before ':')
                bot_token_parts = settings.tg_bot_token.split(':')
                if len(bot_token_parts) < 2:
                    raise ValueError("Invalid bot token format")
                
                # Try to get bot by username or ID
                # For now, we'll use a placeholder since we don't have the bot username
                # In practice, you'd need to resolve the bot from the token
                bot_username = "RustRocketBot"  # This should be configurable or resolved
                
                try:
                    bot_entity = await client.get_entity(bot_username)
                    progress.advance(task)
                except Exception as e:
                    # If bot username doesn't work, we'll skip adding bot for now
                    console.print(Panel(
                        f"⚠️ Could not find bot '@{bot_username}'. Please add the bot manually to the group.",
                        title="Bot Not Found",
                        border_style="yellow"
                    ))
                    logger.warning(f"Could not find bot {bot_username}: {e}")
                    bot_entity = None
                    progress.advance(task)
                
                # Step 3: Add bot as admin (if found)
                if bot_entity:
                    progress.update(task, description="Adding bot as administrator...")
                    
                    # Add bot to the channel
                    await client(functions.channels.InviteToChannelRequest(
                        channel=result.chats[0],
                        users=[bot_entity]
                    ))
                    
                    # Promote bot to admin with necessary rights
                    admin_rights = ChatAdminRights(
                        change_info=True,
                        post_messages=True,
                        edit_messages=True,
                        delete_messages=True,
                        ban_users=True,
                        invite_users=True,
                        pin_messages=True,
                        add_admins=False,  # Don't allow bot to add other admins
                        anonymous=False,
                        manage_call=False,
                        other=False
                    )
                    
                    await client(functions.channels.EditAdminRequest(
                        channel=result.chats[0],
                        user_id=bot_entity,
                        admin_rights=admin_rights,
                        rank="Admin Bot"
                    ))
                    
                    console.print(f"✅ Added bot as administrator")
                    logger.info(f"Added bot as administrator to group {full_chat_id}")
                else:
                    console.print(f"⚠️ Skipped adding bot as administrator")
                
                progress.advance(task)
                
                # Step 4: Output and save chat ID
                progress.update(task, description="Saving chat ID...")
                
                # Print to stdout
                console.print(Panel(
                    f"🆔 Chat ID: [bold green]{full_chat_id}[/bold green]",
                    title="Admin Log Group Created",
                    border_style="green"
                ))
                
                # Copy to clipboard
                try:
                    pyperclip.copy(str(full_chat_id))
                    console.print("📋 Chat ID copied to clipboard!")
                    logger.info(f"Chat ID {full_chat_id} copied to clipboard")
                except Exception as e:
                    logger.warning(f"Failed to copy to clipboard: {e}")
                    console.print("⚠️ Could not copy to clipboard")
                
                # Fallback: write to file
                data_dir = Path("data")
                data_dir.mkdir(exist_ok=True)
                
                chat_id_file = data_dir / "admin_chat_id.txt"
                chat_id_file.write_text(str(full_chat_id))
                console.print(f"💾 Chat ID saved to {chat_id_file}")
                logger.info(f"Chat ID saved to {chat_id_file}")
                
                # Update .env if requested
                if write_env:
                    env_file = Path(".env")
                    if env_file.exists():
                        # Read existing content
                        lines = env_file.read_text().splitlines()
                        
                        # Update or add ADMIN_LOG_CHAT
                        updated = False
                        for i, line in enumerate(lines):
                            if line.startswith("ADMIN_LOG_CHAT="):
                                lines[i] = f"ADMIN_LOG_CHAT={full_chat_id}"
                                updated = True
                                break
                        
                        if not updated:
                            lines.append(f"ADMIN_LOG_CHAT={full_chat_id}")
                        
                        # Write back to file
                        env_file.write_text("\n".join(lines) + "\n")
                        console.print("✅ Updated .env with ADMIN_LOG_CHAT")
                        logger.info(f"Updated .env with ADMIN_LOG_CHAT={full_chat_id}")
                    else:
                        console.print("⚠️ .env file not found, skipped updating")
                        logger.warning(".env file not found for updating")
                
                progress.advance(task)
                
                console.print(Panel(
                    f"🎉 Admin log group '[bold]{group_name}[/bold]' created successfully!\n"
                    f"🆔 Chat ID: {full_chat_id}\n"
                    f"🔒 Group is private and ready for admin logging",
                    title="Success",
                    border_style="green"
                ))
                
            except Exception as e:
                console.print(Panel(
                    f"❌ Failed to create admin log group: {str(e)}",
                    title="Creation Failed",
                    border_style="red"
                ))
                logger.error(f"Failed to create admin log group: {e}")
                raise typer.Exit(1)
                
    except Exception as e:
        console.print(Panel(
            f"❌ Error: {str(e)}",
            title="Error",
            border_style="red"
        ))
        logger.error(f"Admin log creation failed: {e}")
        raise typer.Exit(1)
    finally:
        if client:
            await client.disconnect()


def create_admin_log_command(
    name: str = typer.Option(..., "--name", help="Name for the admin log group"),
    write_env: bool = typer.Option(False, "--write-env", help="Update .env file with ADMIN_LOG_CHAT")
) -> None:
    """Create a private mega-group for admin logging and configure bot access."""
    # TODO: Add support for custom bot username configuration
    # TODO: Add support for setting custom admin permissions
    # TODO: Add support for inviting additional users to the group
    
    logger.info(f"Creating admin log group '{name}' (write_env={write_env})")
    asyncio.run(create_admin_log_group_async(name, write_env)) 