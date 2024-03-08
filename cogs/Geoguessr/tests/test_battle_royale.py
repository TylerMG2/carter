import pytest
from discord import Embed
from discord.ext import commands
from ..battle_royale import BattleRoyale
from ..data import COUNTRIES
from unittest.mock import AsyncMock, MagicMock

HOST_ID = 123
GUESSES = 3
TIME_LIMIT = 120
LOCKIN_TIME = 15

@pytest.fixture
def battle_royale():
    bot = AsyncMock(spec=commands.Bot)
    return BattleRoyale(bot)

# Test constructor method
def test_constructor():
    bot = AsyncMock(spec=commands.Bot)
    battle_royale = BattleRoyale(bot, HOST_ID, GUESSES, TIME_LIMIT, LOCKIN_TIME)
    assert battle_royale.bot is not None
    assert battle_royale.host_id == HOST_ID
    assert battle_royale.guesses == GUESSES
    assert battle_royale.time_limit == TIME_LIMIT
    assert battle_royale.lockin_time == LOCKIN_TIME

# Test with invalid values
@pytest.mark.parametrize('host_id, guesses, time_limit, lockin_time, message', [
    ('', GUESSES, TIME_LIMIT, LOCKIN_TIME, "Invalid host ID"),
    (HOST_ID, 0, TIME_LIMIT, LOCKIN_TIME, "Guesses must be greater than 0"),
    (HOST_ID, GUESSES, 0, LOCKIN_TIME, "Time limit must be between 15 and 600 seconds"),
    (HOST_ID, GUESSES, TIME_LIMIT, -1, "Lockin time cannot be a negative value"),
    (HOST_ID, GUESSES, 601, LOCKIN_TIME, "Time limit must be between 15 and 600 seconds"),
    (HOST_ID, GUESSES, TIME_LIMIT, LOCKIN_TIME+1, "Lockin time cannot be greater than the time limit")
])
def test_invalid_values(host_id, guesses, time_limit, lockin_time, message):
    bot = AsyncMock(spec=commands.Bot)
    with pytest.raises(ValueError) as e:
        BattleRoyale(bot, host_id, guesses, time_limit, lockin_time)
    assert str(e.value) == message

# Test start method
@pytest.mark.asyncio
async def test_start(battle_royale):
    interaction = MagicMock()
    interaction.followup.send = AsyncMock()
    await battle_royale.start(interaction)
    assert battle_royale.pano is not None
    assert battle_royale.timer is None
    interaction.followup.send.assert_called_once()

    # Check that an embed was sent
    _, kwargs = interaction.followup.send.call_args
    assert 'embed' in kwargs
    assert isinstance(kwargs['embed'], Embed)

    # Assert that a panarama was created
    assert battle_royale.pano is not None
    assert battle_royale.pano.iso2 in COUNTRIES

