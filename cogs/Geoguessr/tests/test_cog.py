# # test_main.py
# from ..cog import commands
# from main import bot
# from discord import Embed
# import os
# import pytest
# from unittest.mock import AsyncMock, MagicMock

# # Test challenge command
# @pytest.mark.asyncio
# async def test_challenge_command(bot):

#     interaction = MagicMock()
#     interaction.channel.id = 123
#     interaction.response.send_message = AsyncMock()
#     await bot.tree.get_command('challenge').callback(interaction)

#     # Assert that the response is an embed
#     args, kwargs = interaction.response.send_message.call_args
#     assert isinstance(args[0], Embed)

#     # Assert that the challenge was added to the cog's challenges list
#     assert len(bot.tree.get_cog('Geoguessr').challenges) == 1
