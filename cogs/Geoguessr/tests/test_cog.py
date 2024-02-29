# test_main.py
from ..cog import Geoguessr
from main import bot
from discord import Embed
from discord import app_commands
import os
import pytest
from unittest.mock import AsyncMock, MagicMock

# Cog
cog = Geoguessr(bot)

# Add Geoguessr cog to bot
@pytest.fixture
async def add_geoguessr_cog():
    await bot.add_cog(cog)

# Test challenge command
@pytest.mark.asyncio
async def test_challenge_command(add_geoguessr_cog):
    await add_geoguessr_cog

    interaction = MagicMock()
    interaction.channel_id = 123
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    await bot.tree.get_command('challenge').callback(cog, interaction)

    # Assert that the response was deferred
    interaction.response.defer.assert_called_once_with(thinking=True)

    # Assert that the response is an embed
    _, kwargs = interaction.followup.send.call_args
    assert isinstance(kwargs['embed'], Embed)

    # Assert that the challenge was added to the cog's challenges list
    assert len(cog.challenges.keys()) == 1
    assert 123 in cog.challenges.keys()
