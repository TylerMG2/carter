from utils import EmbedMessage
from discord.ext import commands
from discord import Thread, TextChannel, Interaction
from ..data import get_random_pano
import time
from asyncio import sleep as async_sleep

# Strings
ROUND_LOADING_DESCRIPTION = "## Loading next round...\n### Starting <t:{1:}:R>"
ROUND_DESCRIPTION = "## Round {0:}\n### Ends <t:{1:}:R>\nYou can make a guess with the `/guess` command."
NO_GUESSES_DESCRIPTION = "## Round Ended\nNo one guessed [**:flag_{0:}: {1:}** 🡵]({2:})"
ROUND_OVER_DESCRIPTION = "## Round Ended\nThe correct country was [**:flag_{0:}: {1:}** 🡵]({2:})"
WINNER_DESCRIPTION = "## 🎉 Winner <@{0:}>\n<@{1:}> correctly guessed [**:flag_{2:}: {3:}** 🡵]({4:})"
ROUND_LOAD_TIME = 5

# A class for a battle royale round
class BattleRoyaleRound:

    def __init__(self, bot: commands.Bot, round_time=60, guesses=3, round=1, qualified: list[int] = []):
        self.bot = bot
        self.num_guesses = guesses
        self.round_time = round_time
        self.round = round
        self.embed_message : EmbedMessage = EmbedMessage(bot)
        self.pano = get_random_pano()
        self.all_guesses = set()
        
        # Build guesses dict
        self.guesses : dict[int, list[str]] = {}
        for player in qualified:
            self.guesses[player] = []

    # Function to generate guesses string
    def _generate_guesses_str(self) -> str:
        if len(self.guesses) == 0:
            return "No guesses yet"

        # Build string
        guess_str = ""

        # All guesses
        for guess in self.all_guesses:
            guess_str += f":flag_{guess}: "

        # Each players guessed
        for player_id, guess_list in self.guesses.items():
            guess_str += f"\n<@{player_id}> - "
            for i in range(0, self.num_guesses):
                if i < len(guess_list):
                    if guess_list[i] == self.pano.iso2:
                        guess_str += ":white_check_mark:"
                    else:
                        guess_str += f":flag_{guess_list[i].lower()}:"
                else:
                    guess_str += ":black_small_square:"
        return guess_str
    
    # Function to start the round
    async def start(self, channel: TextChannel):

        # Loading round embed
        future_time = int(time.time() + ROUND_LOAD_TIME)
        self.embed_message.update_embed(description=ROUND_LOADING_DESCRIPTION.format(self.round, future_time), color=0xffff00)
        await self.embed_message.send_to(channel)
        await async_sleep(ROUND_LOAD_TIME)

        # Build challenge embed
        future_time = int(time.time() + self.round_time)
        self.embed_message.update_embed(description=ROUND_DESCRIPTION.format(self.round, future_time), color=0x0000ff)
        self.embed_message.add_field(name='Guesses', value="No guesses yet", inline=False)
        self.embed_message.set_image(url=self.pano.get_image_url())
        await self.embed_message.update()

        # Wait until round end
        await async_sleep(self.round_time)
    
    # Function to handle a guess
    async def guess(self, player_id: int, guess: str) -> bool:
        if player_id not in self.guesses:
            self.guesses[player_id] = []
        
        # Check if the player can guess
        self.guesses[player_id].append(guess)
        self.embed_message.set_field_at(0, name='Guesses', value=self._generate_guesses_str(), inline=False)
        await self.embed_message.update()
        if guess == self.pano.iso2:
            return True
        return False

    async def end(self, winner: int = None):

        # Check if we have a winner
        if winner:
            self.embed_message.update_embed(description=WINNER_DESCRIPTION.format(winner, winner, self.pano.iso2.lower(), self.pano.country, self.pano.get_streetview_url()), color=0x00ff00)
            return await self.embed_message.update()

        self.embed_message.update_embed(description=ROUND_OVER_DESCRIPTION.format(self.pano.iso2.lower(), self.pano.country, self.pano.get_streetview_url()), color=0xff0000)
        await self.embed_message.update()

