from discord.ext import commands
from discord import Interaction
from .user_interfaces import BattleRoyaleSettingsView, BattleRoyaleLobbyView
from utils.embed_message import EmbedMessage
import time
import asyncio
import enum
from .data import COUNTRIES, get_random_pano

# Strings
ROUND_DESCRIPTION = "## Round {0:}\n### Ends <t:{1:}:R>\nYou can make a guess with the `/guess` command."

# Game state enum
class GameState(enum.Enum):
    LOBBY = 1
    ROUND = 2
    BETWEEN_ROUNDS = 3
    WINNER = 4

# Battle royale class
class BattleRoyale:

    # Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_message = EmbedMessage(bot)
        self.settings_view = BattleRoyaleSettingsView()
        self.players : dict[int, int] = {}
        self.host_id : int = None
        self.num_spots : int = 0
        self.qualified : list[int] = []
        self.ended = False
        self.round = 0
        self.state = GameState.LOBBY
        self.guesses : dict[int, list[str]] = {}

    # Starts the setup process for a battle royale
    async def start_setup(self, interaction: Interaction):
        self.host_id = interaction.user.id
        await interaction.response.send_message('# Battle Royale Setup', view=self.settings_view, ephemeral=True)
        await self.settings_view.wait()
        await interaction.delete_original_response()
        if self.settings_view.started:
            await self.create(interaction)

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
    
    # Create the battle royale
    async def create(self, interaction: Interaction):

        # Set details
        self.host_id = interaction.user.id
        self.players[self.host_id] = 0
        self.embed_message.set_author(name=f"{interaction.user.display_name}'s Battle Royale", icon_url=interaction.user.display_avatar.url)
        await self.set_lobby(interaction)

    # Function that sets the state to lobby
    async def set_lobby(self, interaction: Interaction = None):
        self.state = GameState.LOBBY

        # Send the lobby embed
        lobby_view = BattleRoyaleLobbyView(self.players, self.host_id, self.update_players)
        self.embed_message.update_embed(description='# Test', color=0x0000ff)
        self.embed_message.add_field(name='Players', value=self._generate_players_string(), inline=False)
        self.embed_message.add_field(name='Round Time', value=f'{self.settings_view.round_time} seconds', inline=True)
        self.embed_message.add_field(name='Lockin Time', value=f'{self.settings_view.lockin_time} seconds', inline=True)
        self.embed_message.add_field(name='Powerups', value=', '.join(self.settings_view.powerups), inline=False)
        self.embed_message.add_field(name='Lives', value=self.settings_view.lives, inline=True)
        
        # Update the embed message
        if interaction:
            await self.embed_message.respond(interaction, view=lobby_view)
        else:
            await self.embed_message.update()

        # Wait for view to end (should be when the game starts)
        result = await lobby_view.wait()
        if not result:
            self.num_spots = len(self.players.keys())
            self.qualified = list(self.players.keys())
            await self.start_round()
        else:
            await self.embed_message.delete()
            # TODO: Handle battle royale cancelled
    
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

        # Get the panorama
        self.state = GameState.ROUND
        future_time = int(time.time() + self.settings_view.round_time) # Add 0.5 to account for delay
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
        