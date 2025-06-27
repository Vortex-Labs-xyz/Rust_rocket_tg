"""Tests for post scheduler functionality."""

import pytest
from pathlib import Path
from rustrocket_tg.commands.post_scheduler import (
    parse_markdown_file,
    create_inline_keyboard,
)


def test_parse_markdown_file():
    """Test parsing markdown files with YAML front-matter."""
    content = """---
pin: true
buttons:
  - { text: "Start Bot", url: "https://t.me/RustRocketBot?start=request" }
---
👋 Welcome to **Rust Rocket**!
• 25 ms same-block snipes  
• Copy-trade top wallets

🎁 Start the bot & claim **10 RRC** bonus."""

    # Create temporary file
    test_file = Path("/tmp/test_post.md")
    test_file.write_text(content, encoding="utf-8")

    try:
        front_matter, markdown_content = parse_markdown_file(test_file)

        assert front_matter["pin"] is True
        assert len(front_matter["buttons"]) == 1
        assert front_matter["buttons"][0]["text"] == "Start Bot"
        assert (
            front_matter["buttons"][0]["url"]
            == "https://t.me/RustRocketBot?start=request"
        )
        assert "👋 Welcome to **Rust Rocket**!" in markdown_content
    finally:
        test_file.unlink(missing_ok=True)


def test_button_render():
    """Test button rendering for Telethon."""
    buttons_config = [
        {"text": "Start Bot", "url": "https://t.me/RustRocketBot?start=request"}
    ]

    keyboard = create_inline_keyboard(buttons_config)

    assert keyboard is not None
    assert len(keyboard) == 1  # One row
    assert len(keyboard[0]) == 1  # One button in row

    # The button should be a Telethon Button object
    button = keyboard[0][0]
    assert hasattr(button, "text")
    assert hasattr(button, "url")


def test_empty_buttons():
    """Test handling of empty button configuration."""
    keyboard = create_inline_keyboard([])
    assert keyboard is None

    keyboard = create_inline_keyboard(None)
    assert keyboard is None


def test_parse_file_without_frontmatter():
    """Test parsing markdown files without YAML front-matter."""
    content = "Just some markdown content without front-matter."

    test_file = Path("/tmp/test_simple.md")
    test_file.write_text(content, encoding="utf-8")

    try:
        front_matter, markdown_content = parse_markdown_file(test_file)

        assert front_matter == {}
        assert markdown_content == content
    finally:
        test_file.unlink(missing_ok=True)
