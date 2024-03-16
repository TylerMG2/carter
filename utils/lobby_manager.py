from discord import Interaction, Embed, Thread, User, ui, ButtonStyle
from discord.ext import commands
from .embed_message import EmbedMessage
from asyncio import sleep as async_sleep
import enum

LOBBY_DESCRIPTION = "## Lobby\n"
IN_PROGRESS_DESCRIPTION = "## Game In Progress\nYou can still join <#{0:}> to spectate."

class LobbyPlayer:

    def __init__(self, is_host: bool = False) -> None:
        self.is_host = is_host
        self.thread_id : int = -1
        self.score = 0

# Lobby state enum
class LobbyState(enum.Enum):
    LOBBY = 0
    IN_PROGESS = 1

# Lobby view
class LobbyView(ui.View):

    def __init__(self, host_id: int):
        super().__init__()
        self.host_id = host_id
        self.started = False

    @ui.button(label='Settings', emoji='⚙️', style=ButtonStyle.grey, row=0)
    async def settings_button(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id == self.host_id:
            await interaction.response.send_message('Settings', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message('Only the host can change the settings.', ephemeral=True, delete_after=5)
        
    # Close Button
    @ui.button(label='Close', emoji='🗑️', style=ButtonStyle.red, row=0)
    async def close_button(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id == self.host_id:
            await interaction.response.defer()
            self.stop()
        else:
            await interaction.response.send_message('Only the host can delete the game.', ephemeral=True, delete_after=5)

    # Start button
    @ui.button(label='Start', emoji='➡️', style=ButtonStyle.blurple, row=0)
    async def start_button(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id == self.host_id:
            await interaction.response.defer()
            self.started = True
            self.stop()
        else:
            await interaction.response.send_message('Only the host can start the game.', ephemeral=True, delete_after=5)
    
    # Method for cloning this view (Overwrite this for new views)
    def clone(self):
        return self.__class__(self.host_id)

class LobbyManager:

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_message : EmbedMessage = EmbedMessage(bot)
        self.host_id : int = -1
        self.players : dict[int, LobbyPlayer] = {}
        self.state = LobbyState.LOBBY
        self.view : LobbyView = None

    # TODO: Add settings
    async def create_lobby(self, interaction: Interaction, lobby_suffix="Lobby", thread=False, view: LobbyView = None) -> None:
        host = interaction.user
        self.host_id = host.id

        # Add host to players
        self.players[host.id] = LobbyPlayer(is_host=True)

        # Building lobby response (embed and thread)
        self.embed_message.update_embed(title="Building Lobby...", description="This should only be a couple seconds", color=0xffff00)
        await self.embed_message.respond_to(interaction)
        if thread:
            await self.create_thread(f"{host.name}'s {lobby_suffix}")

        # If a view is given, use it
        if view:
            self.view = view
        else:
            self.view = LobbyView(host.id)

        # Lobby embed
        await async_sleep(3)
        self.embed_message.set_author(name=f"{host.name}'s {lobby_suffix}", icon_url=host.avatar.url)
        await self.set_lobby()
    
    # Creates thead with given name
    async def create_thread(self, name: str) -> Thread:
        message = await self.embed_message.get_message()
        thread = await message.create_thread(name=name, auto_archive_duration=60)
        self.thread_id = thread.id
        return thread

    # Returns the active thread
    async def get_thread(self) -> Thread:
        if self.thread_id == -1:
            return None
        return await self.bot.fetch_channel(self.thread_id)

    # Updates the lobby state
    async def update_state(self, state: LobbyState) -> None:
        self.state = state
        await self.embed_message.update()

    # Update the lobby messsage
    async def set_lobby(self) -> None:
        lobby_desc = LOBBY_DESCRIPTION
        if self.thread_id != -1:
            lobby_desc += f"\nJoin <#{self.thread_id}> to participate."

        view = self.view.clone() # Make a copy to ensure a fresh view

        # Set embed
        self.embed_message.update_embed(description=lobby_desc, color=0x0000ff)
        self.embed_message.set_view(view)
        await self.embed_message.update()

        # Wait for the host to start the game
        await self.wait_for_start(view)

    # Function to wait for the lobby to start
    async def wait_for_start(self, view: LobbyView) -> None:
        await view.wait()

        # If the view is stopped (or timeout), close the lobby
        if not view.started:
            self.embed_message.update_embed(title="Lobby Closed", color=0xff0000)
            self.embed_message.remove_author()
            self.embed_message.set_view(None)
            thread = await self.get_thread()
            await thread.delete()
            await self.embed_message.update()
            return
        
        # Start the game
        self.embed_message.update_embed(description=IN_PROGRESS_DESCRIPTION.format(self.thread_id), color=0xffff00)
        self.embed_message.set_view(None)
        await self.embed_message.update()
        await self.start_game()

    # Function to start the game (Override)
    async def start_game(self) -> None:
        pass

        

            