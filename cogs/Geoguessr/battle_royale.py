from discord.ext import commands
from discord import Interaction
from .user_interfaces import BattleRoyaleSettingsView, BattleRoyaleLobbyView
from utils.embed_message import EmbedMessage
import time
import enum

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
        self.state = GameState.LOBBY

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
        self.embed_message.add_field(name='Powerups', value=', '.join(self.settings_view.powerups), inline=True)
        self.embed_message.add_field(name='Lives', value=self.settings_view.lives, inline=False)
        
        # Update the embed message
        if interaction:
            await self.embed_message.respond(interaction, view=lobby_view)
        else:
            await self.embed_message.update()

        # Wait for view to end (should be when the game starts)
        result = await lobby_view.wait()
        if result:
            self.num_spots = len(self.players.keys())
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

        # Loading state
        self.state = GameState.BETWEEN_ROUNDS
        future_time = int(time.time() + 5)
        self.embed_message.update_embed(description=f'## Loading next round <t:{future_time}:R>', color=0xffff00)
        self.embed_message.set_view(None)
        await self.embed_message.update()


        if len(self.qualified) == 0:
            self.qualified = list(self.players.keys())

        # Update num spots
        self.num_spots = len(self.qualified) - 1
        