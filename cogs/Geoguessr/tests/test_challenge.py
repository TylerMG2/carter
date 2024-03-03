from ..challenge import Challenge
from discord import Embed
import pytest
from unittest.mock import AsyncMock, MagicMock

# Test start method
@pytest.mark.asyncio
async def test_start():
    challenge = Challenge()
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction)
    assert challenge.message is not None
    assert challenge.pano is not None
    assert challenge.timer is None
    interaction.followup.send.assert_called_once()

# Test start method with time limit
@pytest.mark.asyncio
async def test_start_time_limit():
    challenge = Challenge()
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction, time_limit=5)
    assert challenge.message is not None
    assert challenge.pano is not None
    assert challenge.timer is not None
    interaction.followup.send.assert_called_once()

    # Close timer
    await challenge.timer.cancel()

# Test make_guess incorrect guess
@pytest.mark.asyncio
async def test_make_guess_incorrect():
    challenge = Challenge()
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction)
    
    # Make an incorrect guess
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    if challenge.pano.iso2 == 'US':
        await challenge.make_guess(interaction, 'CA')
    else:
        await challenge.make_guess(interaction, 'US')
    
    # Assert that the guess was added to the guesses set
    assert len(challenge.guesses) == 1
    assert f":flag_{challenge.pano.iso2.lower()}:" in challenge.guesses
    interaction.response.send_message.assert_called_once_with('Incorrect guess')

# Test make_guess correct guess
@pytest.mark.asyncio
async def test_make_guess_correct():
    challenge = Challenge()
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction)
    
    # Make a correct guess
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    await challenge.make_guess(interaction, challenge.pano.iso2)
    
    # Assert that the guess was added to the guesses set
    interaction.response.send_message.assert_called_once_with('Correct!')

# Test make_guess invalid guess
@pytest.mark.asyncio
async def test_make_guess_invalid():
    challenge = Challenge()
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction)
    
    # Make an invalid guess
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    await challenge.make_guess(interaction, 'AAA')
    
    # Assert that the guess was added to the guesses set
    interaction.response.send_message.assert_called_once_with('Invalid country guess')

# Test end method timout
@pytest.mark.asyncio
async def test_end_timeout():
    challenge = Challenge()
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction, time_limit=5)
    assert challenge.timer is not None

    # End the challenge
    await challenge.end()
    assert challenge.timer is None

    # Check the response embed
    interaction.followup.send.assert_called_once()
    _, kwargs = interaction.followup.send.call_args
    assert isinstance(kwargs['embed'], Embed)
    assert 'Times up!' in kwargs['embed'].title

# Test end method winner
@pytest.mark.asyncio
async def test_end_winner():
    challenge = Challenge()
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction)
    assert challenge.timer is None

    # End the challenge
    await challenge.end(winner=MagicMock())
    assert challenge.timer is None