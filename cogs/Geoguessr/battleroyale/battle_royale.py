from discord.ext import commands
from discord import Interaction
from .settings_view import BattleRoyaleSettingsView
from .battle_royale_round import BattleRoyaleRound
from utils import EmbedMessage, LobbyManager
from ..panorama import Panorama
import time
from asyncio import Task
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
        self.qualified: list[int] = []
        self.next_qualified : list[int] = []
        self.round_task : Task = None

    # Override the start method
    async def start_game(self):
        self.round_task = Task(self.start_round())

    # Function to generate a round
    async def start_round(self, round: int = 1):
        self.current_round = BattleRoyaleRound(self.bot, round_time=self.settings_view.round_time, guesses=self.settings_view.lives, round=round, qualified=self.qualified)
        self.next_qualified = []

        # Post challenge message to the thread
        thread = await self.get_thread()
        if thread is not None:
            await self.current_round.start(thread)
        else:
            raise ValueError("Thread not found")
        
        if len(self.next_qualified) == 0:
            self.next_qualified = self.qualified

        # If we have a winner
        if len(self.next_qualified) == 1:
            await self.current_round.end(winner=self.next_qualified[0])
            await self.set_lobby()
            return
        await self.current_round.end()

        # If there were no guesses. End the challenge
        if len(self.current_round.all_guesses) == 0:
            await self.set_lobby()
            return

        # Start next round
        self.qualified = self.next_qualified
        self.round_task = Task(self.start_round(round=round+1))
    
    # Function to handle a guess
    async def add_guess(self, interaction: Interaction, guess: str):
        guess = guess.lower()
        user_id = interaction.user.id

        # Check if the guess is a valid country
        if (guess.upper() not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            return await interaction.response.send_message(f"Invalid country guess: {guess}", ephemeral=True, delete_after=5)
        
        # Convert guess to iso2
        if guess in COUNTRIES.values():
            for iso2, name in COUNTRIES.items():
                if name.lower().startswith(guess.lower()):
                    guess = iso2
                    break
        guess = guess.upper()

        # Check if we can guess
        if self.current_round == None:
            return await interaction.response.send_message('No active rounds, ask the host to start the game.', ephemeral=True, delete_after=5)
        
        # Check if we qualified
        if user_id not in self.qualified and len(self.qualified) > 0:
            return await interaction.response.send_message("You didn't qualify for this round :(", ephemeral=True, delete_after=5)

        # Check if we already qualified
        if user_id in self.next_qualified:
            return await interaction.response.send_message("You have already qualified", ephemeral=True, delete_after=5)

        # Check if we have used all our guesses
        if user_id in self.current_round.guesses:
            guesses = self.current_round.guesses[user_id]
            if len(guesses) >= self.settings_view.lives:
                return await interaction.response.send_message("You have used all your guesses", ephemeral=True, delete_after=5)
        
        # Add the guess
        correct = await self.current_round.guess(user_id, guess)
        if correct:
            self.next_qualified.append(user_id)
            await interaction.response.send_message("Correct!", ephemeral=True, delete_after=5)

            # Check if the round should be over
            if len(self.next_qualified) == len(self.qualified) - 1 :
                
                # Check if we have a winner
                if len(self.next_qualified) == 1:
                    await self.current_round.end(winner=self.next_qualified[0])
                    self.round_task.cancel()
                    return await self.set_lobby()
                await self.current_round.end()
                self.round_task = Task(await self.start_round(round=self.current_round.round+1))

        else:
            await interaction.response.send_message("Incorrect", ephemeral=True, delete_after=5)