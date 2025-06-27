"""Main CLI application for Rust Rocket TG automation."""

import typer
from rich.console import Console

from .commands.ads_manager import ads_manager_command
from .commands.boost_manager import boost_manager_command
from .commands.create_admin_log import create_admin_log_command
from .commands.leaderboard import leaderboard_command
from .commands.moderation_guard import moderation_guard_command
from .commands.post_scheduler import post_scheduler_command
from .commands.reminder import reminder_command
from .commands.story_uploader import story_uploader_command
from .config import get_settings
from .metrics import ERRORS, LATENCY, RUNS, init_metrics
from .utils.logger import get_logger, setup_logging

# Initialize Prometheus metrics
init_metrics()

app = typer.Typer(
    name="rrx",
    help="Rust Rocket Telegram Channel Boost Automation",
    rich_markup_mode="rich",
)

console = Console()


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
) -> None:
    """Rust Rocket Telegram Channel Boost Automation CLI."""
    with LATENCY.time():
        RUNS.inc()
        try:
            settings = get_settings()
            log_level = "DEBUG" if debug else ("INFO" if verbose else "WARNING")
            setup_logging(settings, level=log_level)

            logger = get_logger()
            logger.debug("CLI initialized with debug logging")

        except Exception as e:
            ERRORS.inc()
            console.print(f"[red]❌ Configuration error: {e}[/red]")
            console.print(
                "[yellow]💡 Make sure your .env file is properly configured[/yellow]"
            )
            raise typer.Exit(1)


# Register all commands with metrics tracking
def track_command(command_func):
    """Decorator to track command execution with Prometheus metrics."""

    def wrapper(*args, **kwargs):
        with LATENCY.time():
            try:
                return command_func(*args, **kwargs)
            except Exception as e:
                ERRORS.inc()
                raise

    return wrapper


# Register all commands
app.command("boost-manager", help="Apply boosts to the configured Telegram channel")(
    track_command(boost_manager_command)
)
app.command("leaderboard", help="Show the top boosters leaderboard")(
    track_command(leaderboard_command)
)
app.command("reminder", help="Send reminder messages for expiring boosts")(
    track_command(reminder_command)
)
app.command(
    "post-scheduler", help="Process and publish scheduled posts from markdown files"
)(track_command(post_scheduler_command))
app.command("story-uploader", help="Upload media files as Telegram stories")(
    track_command(story_uploader_command)
)
app.command(
    "moderation-guard", help="Monitor and maintain channel/group moderation settings"
)(track_command(moderation_guard_command))
app.command("ads-manager", help="Manage Telegram advertising campaigns")(
    track_command(ads_manager_command)
)
app.command("create-admin-log", help="Create a private mega-group for admin logging")(
    track_command(create_admin_log_command)
)


if __name__ == "__main__":
    app()
