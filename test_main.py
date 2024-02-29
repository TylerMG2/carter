# test_main.py
from main import bot
from discord import app_commands
import pytest
from unittest.mock import AsyncMock, MagicMock

# Test that the bot is created
@pytest.mark.asyncio
async def test_bot():
    assert bot is not None

# Test ping command
@pytest.mark.asyncio
async def test_ping_command():
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    await bot.tree.get_command('ping').callback(interaction)
    interaction.response.send_message.assert_called_with('Pong!')
