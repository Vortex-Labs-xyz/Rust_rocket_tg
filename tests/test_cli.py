"""Tests for the CLI application."""

import pytest
from typer.testing import CliRunner

from rustrocket_tg.cli import app

runner = CliRunner()


def test_main_help():
    """Test that the main help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Rust Rocket Telegram Channel Boost Automation" in result.stdout
    assert "boost-manager" in result.stdout
    assert "leaderboard" in result.stdout
    assert "reminder" in result.stdout
    assert "post-scheduler" in result.stdout
    assert "story-uploader" in result.stdout
    assert "moderation-guard" in result.stdout
    assert "ads-manager" in result.stdout
    assert "create-admin-log" in result.stdout


def test_boost_manager_help():
    """Test that boost-manager help command works."""
    result = runner.invoke(app, ["boost-manager", "--help"])
    assert result.exit_code == 0
    assert "Apply boosts to the configured Telegram channel" in result.stdout
    assert "--slots" in result.stdout
    assert "--dry-run" in result.stdout


def test_leaderboard_help():
    """Test that leaderboard help command works."""
    result = runner.invoke(app, ["leaderboard", "--help"])
    assert result.exit_code == 0
    assert "Show the top boosters leaderboard" in result.stdout
    assert "--limit" in result.stdout
    assert "--dry-run" in result.stdout


def test_reminder_help():
    """Test that reminder help command works."""
    result = runner.invoke(app, ["reminder", "--help"])
    assert result.exit_code == 0
    assert "Send reminder messages for expiring boosts" in result.stdout
    assert "--days" in result.stdout
    assert "--dry-run" in result.stdout


def test_verbose_flag():
    """Test that verbose flag is recognized."""
    result = runner.invoke(app, ["--verbose", "--help"])
    assert result.exit_code == 0


def test_debug_flag():
    """Test that debug flag is recognized."""
    result = runner.invoke(app, ["--debug", "--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("command", [
    "boost-manager", 
    "leaderboard", 
    "reminder", 
    "post-scheduler", 
    "story-uploader", 
    "moderation-guard", 
    "ads-manager"
])
def test_all_commands_have_dry_run(command):
    """Test that all commands support dry-run mode."""
    result = runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0
    assert "--dry-run" in result.stdout


def test_boost_manager_with_slots():
    """Test boost-manager command with slots parameter."""
    result = runner.invoke(app, ["boost-manager", "--slots", "2", "--dry-run"])
    # Should succeed in dry-run mode even without full config
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout
    assert "2 boost(s)" in result.stdout


def test_leaderboard_with_limit():
    """Test leaderboard command with limit parameter."""
    result = runner.invoke(app, ["leaderboard", "--limit", "5", "--dry-run"])
    # Should succeed in dry-run mode even without full config
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout
    assert "top 5 boosters" in result.stdout


def test_reminder_with_days():
    """Test reminder command with days parameter."""
    result = runner.invoke(app, ["reminder", "--days", "7", "--dry-run"])
    # Should succeed in dry-run mode even without full config
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout
    assert "7 days" in result.stdout


def test_post_scheduler_help():
    """Test that post-scheduler help command works."""
    result = runner.invoke(app, ["post-scheduler", "--help"])
    assert result.exit_code == 0
    assert "Process and publish scheduled posts" in result.stdout
    assert "--queue-dir" in result.stdout
    assert "--done-dir" in result.stdout
    assert "--dry-run" in result.stdout


def test_story_uploader_help():
    """Test that story-uploader help command works."""
    result = runner.invoke(app, ["story-uploader", "--help"])
    assert result.exit_code == 0
    assert "Upload media files as Telegram stories" in result.stdout
    assert "--queue-dir" in result.stdout
    assert "--done-dir" in result.stdout
    assert "--dry-run" in result.stdout


def test_moderation_guard_help():
    """Test that moderation-guard help command works."""
    result = runner.invoke(app, ["moderation-guard", "--help"])
    assert result.exit_code == 0
    assert "Monitor and maintain channel/group moderation" in result.stdout
    assert "--config" in result.stdout
    assert "--dry-run" in result.stdout


def test_ads_manager_help():
    """Test that ads-manager help command works."""
    result = runner.invoke(app, ["ads-manager", "--help"])
    assert result.exit_code == 0
    assert "Manage Telegram advertising campaigns" in result.stdout
    assert "--queue-dir" in result.stdout
    assert "--done-dir" in result.stdout
    assert "--dry-run" in result.stdout


def test_post_scheduler_dry_run():
    """Test post-scheduler command in dry-run mode."""
    result = runner.invoke(app, ["post-scheduler", "--queue-dir", "content/queue", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout or "No markdown files found" in result.stdout


def test_story_uploader_dry_run():
    """Test story-uploader command in dry-run mode."""
    result = runner.invoke(app, ["story-uploader", "--queue-dir", "story/queue", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout or "No media files found" in result.stdout


def test_moderation_guard_dry_run():
    """Test moderation-guard command in dry-run mode."""
    result = runner.invoke(app, ["moderation-guard", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout


def test_ads_manager_dry_run():
    """Test ads-manager command in dry-run mode."""
    result = runner.invoke(app, ["ads-manager", "--queue-dir", "ads/queue", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout or "No YAML ad configuration files found" in result.stdout


def test_create_admin_log_help():
    """Test that create-admin-log help command works."""
    result = runner.invoke(app, ["create-admin-log", "--help"])
    assert result.exit_code == 0
    assert "Create a private mega-group for admin logging" in result.stdout
    assert "--name" in result.stdout
    assert "--write-env" in result.stdout 