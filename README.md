# Rust Rocket Telegram Automation

A powerful CLI tool for automating Telegram channel boost management, leaderboards, and reminder notifications.

## Features

### Core Automation
- 🚀 **Boost Manager**: Apply boosts to Telegram channels/groups
- 🏆 **Leaderboard**: Display top boosters with rankings
- 📨 **Reminder System**: Send DM reminders for expiring boosts

### Advanced Automation (Phase 2)
- 📝 **Post Scheduler**: Automated posting from markdown files with YAML front-matter
- 📱 **Story Uploader**: Upload media files as Telegram stories with trade event rendering
- 🛡️ **Moderation Guard**: Monitor and maintain channel moderation settings
- 📊 **Ads Manager**: Manage Telegram advertising campaigns from YAML configs
- 🔧 **Admin Log Creator**: Create private mega-groups for admin logging

### Infrastructure
- 🔍 **Dry Run Mode**: Test commands without making actual changes
- 📊 **Rich Console Output**: Beautiful terminal interface
- 🔧 **Configurable**: Environment-based configuration
- 🐳 **Docker Support**: Containerized deployment
- ⏰ **Cron Integration**: Automated scheduling examples

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd rustrocket-tg

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd rustrocket-tg

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your Telegram API credentials:
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   PHONE=your_phone_number
   CHANNEL=@your_channel_or_group
   TG_BOT_TOKEN=optional_bot_token
   SENTRY_DSN=optional_sentry_dsn
   ```

### Getting Telegram API Credentials

1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application to get your `API_ID` and `API_HASH`

## Usage

After installation, you can use the `rrtg` command:

### Boost Manager

Apply boosts to your configured channel:

```bash
# Apply 1 boost (default)
rrtg boost-manager

# Apply multiple boosts
rrtg boost-manager --slots 3

# Test without applying (dry run)
rrtg boost-manager --slots 2 --dry-run
```

### Leaderboard

Show top boosters for your channel:

```bash
# Show top 10 boosters (default)
rrtg leaderboard

# Show top 20 boosters
rrtg leaderboard --limit 20

# Test without querying (dry run)
rrtg leaderboard --dry-run
```

### Reminder System

Send DM reminders for expiring boosts:

```bash
# Check for boosts expiring within 3 days (default)
rrtg reminder

# Check for boosts expiring within 7 days
rrtg reminder --days 7

# Test without sending messages (dry run)
rrtg reminder --days 3 --dry-run
```

### Post Scheduler

Process and publish scheduled posts from markdown files:

```bash
# Process posts from content/queue/ directory
rrtg post-scheduler

# Use custom directories
rrtg post-scheduler --queue-dir my-posts --done-dir published

# Test without publishing (dry run)
rrtg post-scheduler --dry-run
```

### Story Uploader

Upload media files as Telegram stories:

```bash
# Process stories from story/queue/ directory
rrtg story-uploader

# Use custom directories
rrtg story-uploader --queue-dir my-stories --done-dir uploaded

# Test without uploading (dry run)
rrtg story-uploader --dry-run
```

### Moderation Guard

Monitor and maintain channel moderation:

```bash
# Run moderation checks with default config
rrtg moderation-guard

# Use custom Shieldy config file
rrtg moderation-guard --config my-shieldy.json

# Test without making changes (dry run)
rrtg moderation-guard --dry-run
```

### Ads Manager

Manage Telegram advertising campaigns:

```bash
# Process ad campaigns from ads/queue/ directory
rrtg ads-manager

# Use custom directories
rrtg ads-manager --queue-dir my-ads --done-dir processed

# Test without making changes (dry run)
rrtg ads-manager --dry-run
```

### Create Admin Log

Create a private mega-group for admin logging:

```bash
# Create admin log group
rrtg create-admin-log --name "Rust Rocket Admin Log"

# Create and update .env file with chat ID
rrtg create-admin-log --name "My Admin Log" --write-env
```

### Global Options

All commands support these global options:

```bash
# Enable verbose logging
rrtg --verbose boost-manager

# Enable debug logging
rrtg --debug leaderboard

# Get help for any command
rrtg boost-manager --help
rrtg --help
```

## Development

### Setting up for Development

```bash
# Install with development dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .
poetry run black --check .

# Format code
poetry run black .
poetry run ruff --fix .
```

### Project Structure

```
rustrocket_tg/
├── __init__.py
├── config.py              # Pydantic settings management
├── cli.py                 # Main Typer CLI application
├── utils/
│   ├── __init__.py
│   ├── telegram.py        # Telethon client utilities
│   └── logger.py          # Rich logging setup
└── commands/
    ├── __init__.py
    ├── boost_manager.py    # Boost application logic
    ├── leaderboard.py      # Leaderboard display logic
    └── reminder.py         # Reminder system logic
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=rustrocket_tg

# Run specific test file
poetry run pytest tests/test_cli.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_ID` | Yes | Telegram API ID from my.telegram.org |
| `API_HASH` | Yes | Telegram API Hash from my.telegram.org |
| `PHONE` | Yes | Your phone number (with country code) |
| `CHANNEL` | Yes | Target channel/group (@username or ID) |
| `TG_BOT_TOKEN` | No | Bot token for future features |
| `SENTRY_DSN` | No | Sentry DSN for error tracking |
| `SESSION_NAME` | No | Custom session file name (default: premium_user_session) |
| `ADMIN_ID` | No | Admin user ID for moderation alerts |
| `ADMIN_LOG_CHAT` | No | Chat ID for admin logging (set by create-admin-log) |

## Authentication

On first run, the tool will:
1. Prompt for a login code sent to your Telegram account
2. Save the session for future use
3. No need to re-authenticate on subsequent runs

## Troubleshooting

### Common Issues

1. **"Configuration error"**: Check your `.env` file has all required variables
2. **"FloodWait" errors**: The tool automatically handles rate limits
3. **"No boosts available"**: Your account needs Premium subscription with available boost slots

### Debug Mode

Enable debug logging to see detailed information:

```bash
rrtg --debug boost-manager
```

### Dry Run Mode

Test commands without making changes:

```bash
rrtg boost-manager --dry-run
rrtg leaderboard --dry-run
rrtg reminder --dry-run
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Enable debug mode for detailed error information # Release Test Fri Jun 27 12:25:48 CEST 2025
