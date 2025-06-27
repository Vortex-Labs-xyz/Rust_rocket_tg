"""Ads manager command - manages Telegram advertising campaigns via API."""

import asyncio
import shutil
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import get_settings
from ..utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


def load_ad_config(file_path: Path) -> dict[str, Any]:
    """Load advertisement configuration from YAML file."""
    try:
        return yaml.safe_load(file_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML in {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        raise


async def create_or_update_campaign_async(ad_config: dict[str, Any]) -> bool:
    """Create or update a Telegram advertising campaign."""
    try:
        # TODO: Implement actual Telegram Ads API integration
        # This would involve:
        # 1. Authenticate with Telegram Ads API
        # 2. Create or update campaign based on config
        # 3. Set targeting, budget, and creative parameters
        # 4. Return success/failure status

        campaign_name = ad_config.get("campaign_name", "Unknown Campaign")
        budget = ad_config.get("budget", 0)
        target_cpa = ad_config.get("target_cpa", 0)

        logger.info(
            f"Processing campaign: {campaign_name} (budget: ${budget}, target CPA: ${target_cpa})"
        )

        # Simulate API call delay
        await asyncio.sleep(0.2)

        # Placeholder success response
        console.print(f"📊 Campaign processed: {campaign_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to process campaign: {e}")
        return False


async def check_and_pause_campaigns_async(ad_config: dict[str, Any]) -> bool:
    """Check campaign performance and pause if CAC exceeds target."""
    try:
        # TODO: Implement actual performance monitoring
        # This would involve:
        # 1. Fetch current campaign metrics
        # 2. Calculate current CAC (Customer Acquisition Cost)
        # 3. Compare with target CPA
        # 4. Pause ad groups if CAC > target CPA

        campaign_name = ad_config.get("campaign_name", "Unknown Campaign")
        target_cpa = ad_config.get("target_cpa", 0)

        # Simulate performance check
        current_cac = 25.50  # Placeholder - should be fetched from API

        if current_cac > target_cpa:
            # Pause ad groups
            logger.warning(
                f"Campaign {campaign_name}: CAC (${current_cac}) exceeds target CPA (${target_cpa})"
            )
            console.print(
                f"⏸️ Paused {campaign_name}: CAC ${current_cac} > target ${target_cpa}"
            )

            # TODO: Implement actual ad group pausing via API
            return True
        else:
            logger.info(
                f"Campaign {campaign_name}: CAC (${current_cac}) within target CPA (${target_cpa})"
            )
            console.print(
                f"✅ {campaign_name}: CAC ${current_cac} within target ${target_cpa}"
            )
            return True

    except Exception as e:
        logger.error(f"Failed to check campaign performance: {e}")
        return False


async def process_ad_configs_async(
    queue_dir: str = "ads/queue", done_dir: str = "ads/done", dry_run: bool = False
) -> None:
    """Process all YAML ad configuration files in the queue directory."""
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

    yaml_files = list(queue_path.glob("*.yaml")) + list(queue_path.glob("*.yml"))

    if not yaml_files:
        console.print(
            Panel(
                f"📊 No YAML ad configuration files found in {queue_dir}",
                title="No Ads to Process",
                border_style="blue",
            )
        )
        return

    if dry_run:
        console.print(
            Panel(
                f"🔍 DRY RUN: Would process {len(yaml_files)} ad configuration files from {queue_dir}",
                title="Dry Run Mode",
                border_style="blue",
            )
        )
        for file_path in yaml_files:
            try:
                ad_config = load_ad_config(file_path)
                campaign_name = ad_config.get("campaign_name", "Unknown")
                budget = ad_config.get("budget", 0)
                console.print(
                    f"📊 {file_path.name}: {campaign_name} (budget: ${budget})"
                )
            except Exception as e:
                console.print(f"❌ {file_path.name}: Failed to parse - {e}")
        return

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Processing ad campaigns...", total=len(yaml_files)
            )

            processed_count = 0

            for file_path in yaml_files:
                progress.update(task, description=f"Processing {file_path.name}...")

                try:
                    ad_config = load_ad_config(file_path)

                    # Create or update campaign
                    campaign_success = await create_or_update_campaign_async(ad_config)

                    if campaign_success:
                        # Check performance and pause if needed
                        performance_ok = await check_and_pause_campaigns_async(
                            ad_config
                        )

                        if performance_ok:
                            # Move to done directory
                            done_file = done_path / file_path.name
                            shutil.move(str(file_path), str(done_file))

                            processed_count += 1
                            console.print(f"✅ Processed and moved {file_path.name}")
                            logger.info(
                                f"Successfully processed ad config {file_path.name}"
                            )
                        else:
                            console.print(
                                f"⚠️ Performance check failed for {file_path.name}"
                            )
                    else:
                        console.print(
                            f"❌ Failed to process campaign from {file_path.name}"
                        )

                    progress.advance(task)

                except Exception as e:
                    console.print(f"❌ Failed to process {file_path.name}: {e}")
                    logger.error(f"Failed to process {file_path.name}: {e}")
                    continue

            console.print(
                Panel(
                    f"📊 Processed {processed_count} ad campaigns",
                    title="Processing Complete",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", border_style="red"))
        logger.error(f"Ads processing failed: {e}")
        raise typer.Exit(1)


def ads_manager_command(
    queue_dir: str = typer.Option(
        "ads/queue", "--queue-dir", help="Directory to scan for YAML ad configs"
    ),
    done_dir: str = typer.Option(
        "ads/done", "--done-dir", help="Directory to move processed files"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Only show what would be done"
    ),
) -> None:
    """Manage Telegram advertising campaigns from YAML configuration files."""
    # TODO: Add support for campaign analytics and reporting
    # TODO: Add support for A/B testing different ad creatives
    # TODO: Add support for automated budget optimization

    logger.info(f"Starting ads manager (queue_dir={queue_dir}, dry_run={dry_run})")
    asyncio.run(process_ad_configs_async(queue_dir, done_dir, dry_run))
