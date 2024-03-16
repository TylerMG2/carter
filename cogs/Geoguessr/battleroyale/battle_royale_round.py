from utils import EmbedMessage
from discord.ext import commands
from discord import Thread, TextChannel, Interaction
from ..data import get_random_pano
import time
from asyncio import sleep as async_sleep

# Strings
ROUND_DESCRIPTION = "## Round {0:}\n### Ends <t:{1:}:R>\nYou can make a guess with the `/guess` command."
NO_GUESSES_DESCRIPTION = "## Round Ended\nNo one guessed [**:flag_{0:}: {1:}** 🡵]({2:})"
ROUND_OVER_DESCRIPTION = "## Round Ended\nThe correct country was [**:flag_{0:}: {1:}** 🡵]({2:})"
WINNER_DESCRIPTION = "## 🎉 Winner <@{0:}>\n<@{1:}> correctly guessed [**:flag_{2:}: {3:}** 🡵]({4:})"

# A class for a battle royale round
class BattleRoyaleRound:

    def __init__(self, bot: commands.Bot, round_time=60, guesses=3, round=1, qualified: list[int] = []):
        self.bot = bot
        self.num_guesses = guesses
        self.qualified = qualified
        self.round_time = round_time
        self.round = round
        self.embed_message : EmbedMessage = EmbedMessage(bot)
        self.pano = get_random_pano()
        self.next_qualified : list[int] = []
        self.all_guesses = set()
        self.spots = len(qualified) - 1
        
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
            guess_str += f":flag_{guess}:"

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
    async def start(self, channel: Thread | TextChannel) -> bool:

        # Build challenge embed
        future_time = int(time.time() + self.round_time)
        self.pano = get_random_pano()
        self.challenge_message = EmbedMessage(self.bot)
        self.challenge_message.update_embed(description=ROUND_DESCRIPTION.format(round, future_time), color=0x0000ff)
        self.challenge_message.add_field(name='Guesses', value="No guesses yet", inline=False)
        self.challenge_message.set_image(url=self.pano.get_image_url())
        await self.challenge_message.send_to(channel)

        # Wait until round end
        await async_sleep(self.round_time)
        return self.end()
    
    # Function to handle a guess
    async def guess(self, interaction: Interaction, guess: str):
        player_id = interaction.user.id
        if player_id not in self.qualified and len(self.qualified) != 0:
            await interaction.response.send_message("You didn't qualify for this round")

        # If no one qualified, add player to guesses
        if len(self.qualified) == 0:
            self.guesses[player_id] = []

        # Check if the player can guess
        if len(self.guesses[player_id]) < self.num_guesses:
            self.guesses[player_id].append(guess)
            self.all_guesses.add(guess)
            self.challenge_message.set_field_at(0, name='Guesses', value=self._generate_guesses_str())
            await self.challenge_message.update()
            
            # Check if the guess was correct
            if guess == self.pano.iso2 or guess == self.pano.country.lower():
                self.next_qualified.append(player_id)
                self.spots -= 1
                await interaction.response.send_message("Correct!", ephemeral=True, delete_after=5)
            await interaction.response.send_message("Incorrect", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message("You have no more guesses left", ephemeral=True, delete_after=5)
        return False

    async def end(self) -> bool:

        # Check if we have a winner
        if len(self.next_qualified) == 1:
            self.challenge_message.update_embed(description=ROUND_OVER_DESCRIPTION.format(self.next_qualified[0], self.pano.iso2.lower(), self.pano.country, self.pano.get_streetview_url()), color=0x00ff00)
            await self.challenge_message.update()
            return True

        # If no one qualified, qualify everyone
        if len(self.next_qualified) == 0:
            self.qualified = self.next_qualified

        self.challenge_message.update_embed(description=ROUND_OVER_DESCRIPTION.format(self.pano.iso2.lower(), self.pano.country, self.pano.get_streetview_url()), color=0xff0000)
        await self.challenge_message.update()
        return False

