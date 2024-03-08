from discord.ext import commands
from discord import Interaction
from .user_interfaces import BattleRoyaleSettingsView, BattleRoyaleLobbyView
from utils.embed_message import EmbedMessage
from discord.ui import Button

# Battle royale class
class BattleRoyale:

    # Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_message = EmbedMessage(bot)
        self.settings_view = BattleRoyaleSettingsView()
        self.players : dict[int, int] = {}
        self.host_id : int = None
        self.num_places : int = 0

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
            players_string += f"<@{player_id}> - {score}\n"
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

        # Send the lobby embed
        lobby_view = BattleRoyaleLobbyView(self.players, self.host_id)
        self.embed_message.update_embed(description='# Test', color=0x0000ff)
        self.embed_message.add_field(name='Players', value=self._generate_players_string(), inline=False)
        self.embed_message.add_field(name='Current Settings ⚙️', value=f'''Round Time - {self.settings_view.round_time}s
                                    Lockin Time - {self.settings_view.lockin_time}s
                                    Powerups - {', '.join(self.settings_view.powerups)}
                                    Guesses - {self.settings_view.guesses}
                                     ''', inline=False)
        
        # Update the embed message
        if interaction:
            await self.embed_message.respond(interaction, view=lobby_view)
        else:
            await self.embed_message.update()

        # Wait for view to end
        result = await lobby_view.wait()