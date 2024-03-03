# test_main.py
from ..cog import Geoguessr
from ..challenge import Challenge
from main import bot
from discord import Embed
import pytest
from unittest.mock import AsyncMock, MagicMock

# Fix to create a new instance of the cog for each test
@pytest.fixture
def cog():
    return Geoguessr(bot)

# Test challenge command
@pytest.mark.asyncio
async def test_challenge_command(cog: Geoguessr):

    interaction = MagicMock()
    interaction.channel_id = 123
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    await cog.challenge.callback(cog, interaction)

    # Assert that the response was deferred
    interaction.response.defer.assert_called_once_with(thinking=True)

    # Assert that the response is an embed
    _, kwargs = interaction.followup.send.call_args
    assert isinstance(kwargs['embed'], Embed)

    # Assert that the challenge was added to the cog's challenges list
    assert len(cog.challenges.keys()) == 1
    assert 123 in cog.challenges.keys()
    assert isinstance(cog.challenges[123], Challenge)
    assert cog.challenges[123].pano is not None

# Test challenge command with time limit
@pytest.mark.asyncio
async def test_challenge_command_time_limit(cog: Geoguessr):

    interaction = MagicMock()
    interaction.channel_id = 123
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    await cog.challenge.callback(cog, interaction, timer=5)

    # Check the timer
    assert cog.challenges[123].timer is not None
    assert cog.challenges[123].timer.done() == False

    # Close timer
    cog.challenges[123].timer.cancel()

# Test guess command
@pytest.mark.asyncio
async def test_guess_command(cog: Geoguessr):

    interaction = MagicMock()
    interaction.channel_id = 123
    interaction.response.send_message = AsyncMock()
    await cog.guess.callback(cog, interaction, country='US')

    # Assert that the challenge exists
    assert 123 in cog.challenges.keys()

    # Assert that the guess was added to the challenge
    assert len(cog.challenges[123].guesses) == 1
    assert f":flag_us:" in cog.challenges[123].guesses
    interaction.response.send_message.assert_called_once()

    # Check the message response
    args, _ = interaction.response.send_message.call_args
    assert 'Incorrect guess' in args[0]