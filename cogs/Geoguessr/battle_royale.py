from discord.ext import commands
from discord import Interaction
from .user_interfaces import BattleRoyaleSettingsView
from utils.embed_message import EmbedMessage

# Battle royale class
class BattleRoyale:

    # Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_message = EmbedMessage(bot)
        self.settings_view = BattleRoyaleSettingsView(self)
        self.host_id : int = None

    # Starts the setup process for a battle royale
    async def start_setup(self, interaction: Interaction):
        self.host_id = interaction.user.id
        await interaction.response.send_message('Starting battle royale setup...', view=self.settings_view, ephemeral=True)
    
    # Create the battle royale
    async def create(self, interaction: Interaction):
        self.embed_message.update_embed(description='Test', color=0x0000ff)
        self.embed_message.set_author(name=f"{interaction.user.display_name}'s Battle Royale", icon_url=interaction.user.display_avatar.url)
        await self.embed_message.respond(interaction)