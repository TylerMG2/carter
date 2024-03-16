from discord.ext import commands
from discord import Interaction
from .settings_view import BattleRoyaleSettingsView
from .battle_royale_round import BattleRoyaleRound
from utils import EmbedMessage, LobbyManager
from ..panorama import Panorama
import time
import asyncio
import enum
from ..data import COUNTRIES, get_random_pano

# Strings


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
        self.current_round : BattleRoyaleRound = None

    # Override the start method
    async def start_game(self):
        await self.start_round()

    # Function to generate a round
    async def start_round(self, qualified: list[int] = [], round: int = 1):
        self.current_round = BattleRoyaleRound(self.bot, round_time=self.settings_view.round_time, guesses=self.settings_view.lives, round=round, qualified=qualified)

        # Post challenge message to the thread
        thread = await self.get_thread()
        result = False
        if thread is not None:
            result = await self.current_round.start(thread)
        else:
            raise ValueError("Thread not found")
        
        # If a winner was found
        if result:
            await self.set_lobby()
            return
        
        # Reset the round
        await self.start_round(self.current_round.qualified, round+1)
    
    # Function to handle a guess
    async def make_guess(self, interaction: Interaction, guess: str):
        guess = guess.lower()

        # Check if the guess is a valid country
        if (guess.upper() not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            raise ValueError(f"Invalid country guess: {guess}")
        
        # Convert guess to iso2
        if guess in COUNTRIES.values():
            for iso2, name in COUNTRIES.items():
                if name.lower().startswith(guess.lower()):
                    guess = iso2
                    break

        # Check if we can guess
        if self.current_round == None:
            await interaction.response.send_message('No active rounds, ask the host to start the game.', ephemeral=True, delete_after=5)
            return
        
        await self.current_round.guess(interaction)