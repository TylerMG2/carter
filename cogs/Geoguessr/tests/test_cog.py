# test_main.py
from ..cog import commands
from main import bot
from discord import Embed
import pytest
from unittest.mock import AsyncMock, MagicMock

# Test challenge command
@pytest.mark.asyncio
async def test_challenge_command():
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    await bot.tree.get_command('challenge').callback(interaction)

    # Assert that the response is an embed
    args, kwargs = interaction.response.send_message.call_args
    assert isinstance(args[0], Embed)