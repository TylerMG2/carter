from discord.ext import commands
from discord import Interaction
from .user_interfaces import BattleRoyaleSettingsView
from utils import EmbedMessage
import time
import asyncio
import enum
from .data import COUNTRIES, get_random_pano

# Strings
LOBBY_DESCRIPTION = "## {0:}\nJoin the thread below to participate."
ROUND_DESCRIPTION = "## Round {0:}\n### Ends <t:{1:}:R>\nYou can make a guess with the `/guess` command."

# Game state enum
class GameState(enum.Enum):
    LOBBY = 1
    ROUND = 2
    BETWEEN_ROUNDS = 3
    WINNER = 4

# Battle royale class
class BattleRoyaleLobby:

    # Constructor
    def __init__(self, embed_message: EmbedMessage):
        self.embed_message = embed_message
        self.settings_view = BattleRoyaleSettingsView()
        self.players : dict[int, int] = {}
        self.host_id = -1
        self.num_spots : int = 0
        self.qualified : list[int] = []
        self.ended = False
        self.round = 0
        self.state = GameState.LOBBY
        self.guesses : dict[int, list[str]] = {}
        self.thread_id = -1

    # Function to create the battle royale
    async def create(self, interaction: Interaction):
        self.host_id = interaction.user.id

        # Build lobby embed
        self.embed_message.update_embed(description=LOBBY_DESCRIPTION.format("Waiting for host..."), color=0x0000ff)
        self.embed_message.set_author(name=f"{interaction.user.name}'s Battle Royale Lobby", icon_url=interaction.user.avatar.url)
        self.embed_message.add_field(name='Leaderboard', value=self._generate_players_string(), inline=False)
        self.embed_message.add_field(name='Round Time', value=f'{self.settings_view.round_time} seconds', inline=True)
        self.embed_message.add_field(name='Lockin Time', value=f'{self.settings_view.lockin_time} seconds', inline=True)
        self.embed_message.add_field(name='Powerups', value=', '.join(self.settings_view.powerups), inline=True)
        self.embed_message.add_field(name='Lives', value=self.settings_view.lives, inline=True)
        await self.embed_message.respond(interaction, view=BattleRoyaleLobbyView(self.host_id))

        # Create thread for posting rounds
        message = await self.embed_message.get_message()
        thread = await message.create_thread(name=f"{interaction.user.name}'s Battle Royale Lobby", auto_archive_duration=60)
        self.thread_id = thread.id

    # Function to generate players string
    def _generate_players_string(self) -> str:
        players_string = ""
        for player_id, score in self.players.items():
            players_string += f"<@{player_id}> - {score}"
            if player_id == self.host_id:
                players_string += " 👑"
            players_string += "\n"
        return players_string

    # Function to generate the guesses string
    def _generate_guesses_string(self) -> str:
        guesses_string = ""
        for player_id in self.guesses:
            emojis = []
            for guess in self.guesses[player_id]:
                
                # If the guess is correct, add a green checkmark
                if guess == self.pano.iso2.lower() or guess == self.pano.country.lower():
                    emojis.append(":white_check_mark:")
                else:
                    emojis.append(f":flag_{guess}:")

            for i in range(len(emojis), self.settings_view.lives):
                emojis.append(":black_small_square:")
            guesses_string += f"<@{player_id}> {' '.join(emojis)}\n"
        return guesses_string
    
    # Function to update players
    async def update_players(self):
        if self.state == GameState.LOBBY:
            self.embed_message.set_field_at(0, name='Players', value=self._generate_players_string(), inline=False)
            await self.embed_message.update()

    # Function to start a round
    async def start_round(self):
        self.round += 1
        self.guesses = {}
        for player_id in self.qualified:
            self.guesses[player_id] = []
        self.qualified = []

        # Loading state
        self.state = GameState.BETWEEN_ROUNDS
        future_time = int(time.time() + 5)
        self.embed_message.update_embed(description=f'## Loading next round <t:{future_time}:R>', color=0xffff00)
        self.embed_message.set_view(None)
        await self.embed_message.update(now=True)
        await asyncio.sleep(5)

        # Build challenge embed
        self.state = GameState.ROUND
        future_time = int(time.time() + self.settings_view.round_time)
        self.pano = get_random_pano()
        self.embed_message.update_embed(description=ROUND_DESCRIPTION.format(self.round, future_time), color=0x0000ff)
        self.embed_message.add_field(name='Guesses', value=self._generate_guesses_string(), inline=False)
        self.embed_message.set_image(url=self.pano.get_image_url())
        await self.embed_message.update(now=True)
        print(self.pano.iso2)
        await asyncio.sleep(self.settings_view.round_time)

        if len(self.qualified) == 0:
            self.qualified = list(self.players.keys())

        # Update num spots
        self.num_spots = len(self.qualified) - 1
    
    # Function to handle a guess
    async def player_guess(self, interaction: Interaction, guess: str):
        guess = guess.lower()

        # Check if the guess is a valid country
        if (guess.upper() not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            raise ValueError(f"Invalid country guess: {guess}")

        # Check if we can guess
        if self.state != GameState.ROUND:
            await interaction.response.send_message('The game hasn\'t started yet', ephemeral=True, delete_after=5)
            return
        if interaction.user.id not in self.guesses:
            await interaction.response.send_message('You didn\'t qualify for this round', ephemeral=True, delete_after=5)
            return
        if len(self.guesses[interaction.user.id]) >= self.settings_view.lives:
            await interaction.response.send_message('You are out of guesses', ephemeral=True, delete_after=5)
            return
        if interaction.user.id in self.qualified:
            await interaction.response.send_message('You have already qualified for the next round', ephemeral=True, delete_after=5)
            return
        
        # Check if the guess is correct
        self.guesses[interaction.user.id].append(guess)
        if guess == self.pano.iso2.lower() or guess == self.pano.country.lower():
            await interaction.response.send_message('Correct guess', ephemeral=True, delete_after=5)
            self.qualified.append(interaction.user.id)
        else:
            await interaction.response.send_message('Incorrect guess', ephemeral=True, delete_after=5)
        self.embed_message.set_field_at(0, name='Guesses', value=self._generate_guesses_string(), inline=False)
        await self.embed_message.update()
        