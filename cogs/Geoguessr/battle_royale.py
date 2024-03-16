from discord.ext import commands
from discord import Interaction
from .user_interfaces import BattleRoyaleSettingsView
from utils import EmbedMessage, LobbyManager
from .panorama import Panorama
import time
import asyncio
import enum
from .data import COUNTRIES, get_random_pano

# Strings
LOBBY_DESCRIPTION = "## {0:}\nJoin the thread below to participate."
ROUND_DESCRIPTION = "## Round {0:}\n### Ends <t:{1:}:R>\nYou can make a guess with the `/guess` command."
ROUND_OVER_DESCRIPTION = "## Round Ended\nThe correct country was [**:flag_{0:}: {1:}** 🡵]({2:})"

# Game state enum
class GameState(enum.Enum):
    LOBBY = 1
    ROUND = 2
    BETWEEN_ROUNDS = 3
    WINNER = 4

# Battle royale class
class BattleRoyaleLobby(LobbyManager):

    # Constructor
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.settings_view = BattleRoyaleSettingsView() # TODO: Give the user the ability to change the settings
        self.pano : Panorama = None
        self.challenge_message : EmbedMessage = None
        self.current_round = None

    # Override the start method
    async def start_game(self):
        await self.start_round()

    # Function to generate a round
    async def start_round(self, qualified: list[int] = [], round: int = 1, num_spots: int = -1):

        # Build challenge embed
        future_time = int(time.time() + self.settings_view.round_time)
        self.pano = get_random_pano()
        self.challenge_message = EmbedMessage(self.bot)
        self.challenge_message.update_embed(description=ROUND_DESCRIPTION.format(round, future_time), color=0x0000ff)
        self.challenge_message.add_field(name='Guesses', value="No guesses yet", inline=False)
        self.challenge_message.set_image(url=self.pano.get_image_url())

        # Post challenge message to the thread
        thread = await self.get_thread()
        if thread is not None:
            await self.challenge_message.send_to(thread)


        print(self.pano.iso2)
        await asyncio.sleep(10)

        # End the round
        self.challenge_message.update_embed(description=ROUND_OVER_DESCRIPTION.format(self.pano.iso2.lower(), self.pano.country, self.pano.get_streetview_url()), color=0xff0000)
        await self.challenge_message.update()



        # self.round += 1
        # self.guesses = {}
        # for player_id in self.qualified:
        #     self.guesses[player_id] = []
        # self.qualified = []

        # # Loading state
        # self.state = GameState.BETWEEN_ROUNDS
        # future_time = int(time.time() + 5)
        # self.embed_message.update_embed(description=f'## Loading next round <t:{future_time}:R>', color=0xffff00)
        # self.embed_message.set_view(None)
        # await self.embed_message.update(now=True)
        # await asyncio.sleep(5)

        

        # if len(self.qualified) == 0:
        #     self.qualified = list(self.players.keys())

        # # Update num spots
        # self.num_spots = len(self.qualified) - 1
    
    # Function to handle a guess
    # async def player_guess(self, interaction: Interaction, guess: str):
    #     guess = guess.lower()

    #     # Check if the guess is a valid country
    #     if (guess.upper() not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
    #         raise ValueError(f"Invalid country guess: {guess}")

    #     # Check if we can guess
    #     if self.state != GameState.ROUND:
    #         await interaction.response.send_message('The game hasn\'t started yet', ephemeral=True, delete_after=5)
    #         return
    #     if interaction.user.id not in self.guesses:
    #         await interaction.response.send_message('You didn\'t qualify for this round', ephemeral=True, delete_after=5)
    #         return
    #     if len(self.guesses[interaction.user.id]) >= self.settings_view.lives:
    #         await interaction.response.send_message('You are out of guesses', ephemeral=True, delete_after=5)
    #         return
    #     if interaction.user.id in self.qualified:
    #         await interaction.response.send_message('You have already qualified for the next round', ephemeral=True, delete_after=5)
    #         return
        
    #     # Check if the guess is correct
    #     self.guesses[interaction.user.id].append(guess)
    #     if guess == self.pano.iso2.lower() or guess == self.pano.country.lower():
    #         await interaction.response.send_message('Correct guess', ephemeral=True, delete_after=5)
    #         self.qualified.append(interaction.user.id)
    #     else:
    #         await interaction.response.send_message('Incorrect guess', ephemeral=True, delete_after=5)
    #     self.embed_message.set_field_at(0, name='Guesses', value=self._generate_guesses_string(), inline=False)
    #     await self.embed_message.update()
        