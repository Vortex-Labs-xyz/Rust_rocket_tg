"""Tests for the create-admin-log command."""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from typer.testing import CliRunner

from rustrocket_tg.cli import app

runner = CliRunner()


@pytest.fixture
def mock_settings():
    """Mock settings with required values."""
    settings = MagicMock()
    settings.api_id = 123456
    settings.api_hash = "test_hash"
    settings.phone = "+1234567890"
    settings.channel = "@test_channel"
    settings.tg_bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    settings.session_name = "test_session"
    return settings


@pytest.fixture
def mock_telethon_result():
    """Mock Telethon CreateChannelRequest result."""
    chat = MagicMock()
    chat.id = 1234567890

    result = MagicMock()
    result.chats = [chat]
    return result


class TestCreateAdminLogCommand:
    """Test suite for create-admin-log command."""

    def test_create_admin_log_help(self):
        """Test that help command works correctly."""
        result = runner.invoke(app, ["create-admin-log", "--help"])
        assert result.exit_code == 0
        assert "Create a private mega-group for admin logging" in result.stdout
        assert "--name" in result.stdout
        assert "--write-env" in result.stdout

    @patch("rustrocket_tg.commands.create_admin_log.get_settings")
    @patch("rustrocket_tg.commands.create_admin_log.get_authenticated_client")
    @patch("rustrocket_tg.commands.create_admin_log.pyperclip")
    def test_create_admin_log_without_bot_token(
        self, mock_pyperclip, mock_client, mock_settings_func
    ):
        """Test command fails gracefully when TG_BOT_TOKEN is missing."""
        # Setup
        settings = MagicMock()
        settings.tg_bot_token = None
        mock_settings_func.return_value = settings

        # Execute
        result = runner.invoke(app, ["create-admin-log", "--name", "Test Group"])

        # Assert
        assert result.exit_code == 1
        assert "TG_BOT_TOKEN is required" in result.stdout

    @patch("rustrocket_tg.commands.create_admin_log.get_settings")
    @patch("rustrocket_tg.commands.create_admin_log.get_authenticated_client")
    @patch("rustrocket_tg.commands.create_admin_log.pyperclip")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    def test_create_admin_log_success_without_bot(
        self,
        mock_write_text,
        mock_mkdir,
        mock_pyperclip,
        mock_client_func,
        mock_settings_func,
        mock_settings,
        mock_telethon_result,
    ):
        """Test successful group creation when bot is not found."""
        # Setup
        mock_settings_func.return_value = mock_settings

        mock_client = AsyncMock()
        mock_client_func.return_value = mock_client

        # Mock Telethon calls
        mock_client.return_value = mock_telethon_result
        mock_client.get_entity.side_effect = Exception("Bot not found")

        # Mock pyperclip
        mock_pyperclip.copy.return_value = None

        # Execute
        result = runner.invoke(app, ["create-admin-log", "--name", "Test Group"])

        # Assert
        assert result.exit_code == 0
        assert "Created mega-group: Test Group" in result.stdout
        assert "Could not find bot" in result.stdout
        assert "Chat ID copied to clipboard!" in result.stdout

        # Verify file operations
        mock_mkdir.assert_called()
        mock_write_text.assert_called()
        mock_pyperclip.copy.assert_called_with("-1001001234567890")

    @patch("rustrocket_tg.commands.create_admin_log.get_settings")
    @patch("rustrocket_tg.commands.create_admin_log.get_authenticated_client")
    @patch("rustrocket_tg.commands.create_admin_log.pyperclip")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_create_admin_log_with_env_update(
        self,
        mock_exists,
        mock_read_text,
        mock_write_text,
        mock_mkdir,
        mock_pyperclip,
        mock_client_func,
        mock_settings_func,
        mock_settings,
        mock_telethon_result,
    ):
        """Test group creation with .env file update."""
        # Setup
        mock_settings_func.return_value = mock_settings

        mock_client = AsyncMock()
        mock_client_func.return_value = mock_client
        mock_client.return_value = mock_telethon_result
        mock_client.get_entity.side_effect = Exception("Bot not found")

        # Mock .env file operations
        mock_exists.return_value = True
        mock_read_text.return_value = "API_ID=123\nAPI_HASH=test\nPHONE=+123\n"

        # Execute
        result = runner.invoke(
            app, ["create-admin-log", "--name", "Test Group", "--write-env"]
        )

        # Assert
        assert result.exit_code == 0
        assert "Updated .env with ADMIN_LOG_CHAT" in result.stdout

        # Verify .env was updated
        mock_write_text.assert_called()
        write_call_args = mock_write_text.call_args_list

        # Find the .env write call (not the data file write call)
        env_write_call = None
        for call in write_call_args:
            if "ADMIN_LOG_CHAT=" in str(call):
                env_write_call = call
                break

        assert env_write_call is not None
        assert "ADMIN_LOG_CHAT=-1001001234567890" in str(env_write_call)

    @patch("rustrocket_tg.commands.create_admin_log.get_settings")
    @patch("rustrocket_tg.commands.create_admin_log.get_authenticated_client")
    @patch("rustrocket_tg.commands.create_admin_log.pyperclip")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    def test_create_admin_log_with_bot_success(
        self,
        mock_write_text,
        mock_mkdir,
        mock_pyperclip,
        mock_client_func,
        mock_settings_func,
        mock_settings,
        mock_telethon_result,
    ):
        """Test successful group creation with bot addition."""
        # Setup
        mock_settings_func.return_value = mock_settings

        mock_client = AsyncMock()
        mock_client_func.return_value = mock_client
        mock_client.return_value = mock_telethon_result

        # Mock successful bot entity retrieval
        mock_bot_entity = MagicMock()
        mock_client.get_entity.return_value = mock_bot_entity

        # Execute
        result = runner.invoke(app, ["create-admin-log", "--name", "Test Group"])

        # Assert
        assert result.exit_code == 0
        assert "Created mega-group: Test Group" in result.stdout
        assert "Added bot as administrator" in result.stdout

        # Verify bot was added and promoted
        mock_client.assert_called()  # CreateChannelRequest called
        assert mock_client.call_count >= 3  # CreateChannel, InviteToChannel, EditAdmin

    @patch("rustrocket_tg.commands.create_admin_log.get_settings")
    @patch("rustrocket_tg.commands.create_admin_log.get_authenticated_client")
    def test_create_admin_log_telethon_error(
        self, mock_client_func, mock_settings_func, mock_settings
    ):
        """Test command handles Telethon errors gracefully."""
        # Setup
        mock_settings_func.return_value = mock_settings
        mock_client_func.side_effect = Exception("Connection failed")

        # Execute
        result = runner.invoke(app, ["create-admin-log", "--name", "Test Group"])

        # Assert
        assert result.exit_code == 1
        assert "Error:" in result.stdout

    def test_create_admin_log_missing_name(self):
        """Test command requires --name parameter."""
        result = runner.invoke(app, ["create-admin-log"])
        assert (
            result.exit_code == 2
        )  # Typer returns exit code 2 for missing required options

    @patch("rustrocket_tg.commands.create_admin_log.get_settings")
    @patch("rustrocket_tg.commands.create_admin_log.get_authenticated_client")
    @patch("rustrocket_tg.commands.create_admin_log.pyperclip")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.exists")
    def test_create_admin_log_env_file_not_found(
        self,
        mock_exists,
        mock_write_text,
        mock_mkdir,
        mock_pyperclip,
        mock_client_func,
        mock_settings_func,
        mock_settings,
        mock_telethon_result,
    ):
        """Test behavior when .env file doesn't exist but --write-env is used."""
        # Setup
        mock_settings_func.return_value = mock_settings

        mock_client = AsyncMock()
        mock_client_func.return_value = mock_client
        mock_client.return_value = mock_telethon_result
        mock_client.get_entity.side_effect = Exception("Bot not found")

        # Mock .env file not existing
        mock_exists.return_value = False

        # Execute
        result = runner.invoke(
            app, ["create-admin-log", "--name", "Test Group", "--write-env"]
        )

        # Assert
        assert result.exit_code == 0
        assert ".env file not found, skipped updating" in result.stdout
