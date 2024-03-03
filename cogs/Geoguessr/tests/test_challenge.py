from ..challenge import Challenge
from discord import Embed
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def challenge():
    bot = MagicMock()
    bot.get_channel = AsyncMock()
    return Challenge(AsyncMock())

# Test start method
@pytest.mark.asyncio
async def test_start(challenge):
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction)
    assert challenge.pano is not None
    assert challenge.timer is None
    interaction.followup.send.assert_called_once()

# Test start method with time limit
@pytest.mark.asyncio
async def test_start_time_limit(challenge):
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await challenge.start(interaction, time_limit=5)
    assert challenge.pano is not None
    assert challenge.timer is not None
    assert challenge.timer.done() == False
    interaction.followup.send.assert_called_once()

    # Close timer
    challenge.timer.cancel()

# # Test make_guess incorrect guess
# @pytest.mark.asyncio
# async def test_make_guess_incorrect(challenge):
#     interaction = MagicMock()
#     interaction.followup.send = AsyncMock()
#     await challenge.start(interaction)
    
#     # Make an incorrect guess
#     interaction = MagicMock()
#     interaction.response.send_message = AsyncMock()
#     if challenge.pano.iso2 == 'US':
#         await challenge.make_guess(interaction, 'CA')
#     else:
#         await challenge.make_guess(interaction, 'US')
    
#     # Assert that the guess was added to the guesses set
#     assert len(challenge.guesses) == 1
#     assert f":flag_us:" in challenge.guesses or f":flag_ca:" in challenge.guesses
#     interaction.response.send_message.assert_called_once()

#     # Check the message response
#     args, _ = interaction.response.send_message.call_args
#     assert 'Incorrect guess' in args[0]

# # Test make_guess correct guess
# @pytest.mark.asyncio
# async def test_make_guess_correct(challenge):
#     interaction = MagicMock()
#     interaction.followup.send = AsyncMock()
#     await challenge.start(interaction)
    
#     # Make a correct guess
#     interaction = MagicMock()
#     interaction.response.send_message = AsyncMock()
#     await challenge.make_guess(interaction, challenge.pano.iso2)
    
#     # Assert that the guess was added to the guesses set
#     interaction.response.send_message.assert_called_once()

#     # Check the message response
#     args, _ = interaction.response.send_message.call_args
#     assert 'Correct' in args[0]

# # Test guessing with the name of the country
# @pytest.mark.asyncio
# async def test_make_guess_name(challenge):
#     interaction = MagicMock()
#     interaction.followup.send = AsyncMock()
#     await challenge.start(interaction)
    
#     # Make a correct guess
#     interaction = MagicMock()
#     interaction.response.send_message = AsyncMock()
#     await challenge.make_guess(interaction, challenge.pano.country)
    
#     # Assert that the guess was added to the guesses set
#     interaction.response.send_message.assert_called_once()

#     # Check the message response
#     args, _ = interaction.response.send_message.call_args
#     assert 'Correct' in args[0]

# # Test make_guess invalid guess
# @pytest.mark.asyncio
# async def test_make_guess_invalid(challenge):
#     interaction = MagicMock()
#     interaction.followup.send = AsyncMock()
#     await challenge.start(interaction)
    
#     # Make an invalid guess
#     interaction = MagicMock()
#     interaction.response.send_message = AsyncMock()
#     await challenge.make_guess(interaction, 'AAA')
    
#     # Assert that the guess was added to the guesses set
#     interaction.response.send_message.assert_called_once()
#     args, _ = interaction.response.send_message.call_args
#     assert 'Invalid country guess' in args[0]

# # Test end method timout
# @pytest.mark.asyncio
# async def test_end_timeout(challenge):
#     interaction = MagicMock()
#     interaction.followup.send = AsyncMock()
#     await challenge.start(interaction, time_limit=5)

#     # End the challenge
#     await challenge.end()
#     assert challenge.timer.cancelling()

# # Test end method winner
# @pytest.mark.asyncio
# async def test_end_winner(challenge):
#     interaction = MagicMock()
#     interaction.followup.send = AsyncMock()
#     await challenge.start(interaction)
#     assert challenge.timer is None

#     # End the challenge
#     await challenge.end(winner=MagicMock())