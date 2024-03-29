from discord import Interaction, Embed, Message, User, WebhookMessage, ui, TextChannel
from discord.ext import commands
import asyncio

# This class is used to manage the creation, editing and deletion of embeds
#TODO: Add some errors for when the message_id or channel_id is not set
class EmbedMessage(Embed):

    """
    A extension class of discordpy Embed used to manage a single embed message.
    Call update after editing the embed message to update the message.

    ...

    Attributes
    ----------
    bot : commands.Bot
        a discord bot instance
    author_id : int
        the id of the author of the embed message
    message_id : int
        the id of the embed message
    channel_id : int
        the id of the channel where the embed message is located
    embed : Embed
        an embed message

    Methods
    -------
    create(title: str, description: str, color: int) -> Embed
        Creates a new embed message
    send(channel_id: int) -> None
        Sends the embed message to a channel
    get_message() -> Message
        Gets the embed message
    get_author() -> User
        Gets the author of the embed message
    update() -> None
        Updates the embed message
    delete() -> None
        Deletes the embed message
    
    """
    FOOTER_TEXT = "| Bot by @tmg1"

    # Constructor
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.view : ui.View = None
        self.author_id = None
        self.message_id = None
        self.channel_id = None
        self.update_task : asyncio.Task = None

    # Function to get the embed message
    async def get_message(self) -> Message:

        # Validate message and channel id
        if self.message_id is None or self.channel_id is None:
            raise ValueError("Message or channel id not set")
        channel = self.bot.get_channel(self.channel_id)

        # Validate channel
        if channel is None:
            raise ValueError("Channel not found")

        return await channel.fetch_message(self.message_id)
    
    # Function to get the author of the embed message
    async def _get_author(self) -> User:
        if self.author_id is None:
            return None
        author = await self.bot.fetch_user(self.author_id)
        return author
    
    # Function to update the author of the embed message
    def update_author(self, author: User) -> None:

        # No author, set bot as the author
        if author is None:
            self.author_id = None
            self.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)
            return
        
        # Update the author_id and the embed message
        self.author_id = author.id
        self.set_author(name=author.display_name, icon_url=author.display_avatar.url)
    
    # Function to update the view
    def set_view(self, view: ui.View) -> None:
        self.view = view
    
    # Function to reset current embed values and set new valies
    def update_embed(self, title: str = None, description: str = None, color: int = 0x00ff00) -> Embed:

        # Retain author
        author = self.author
        self.clear_fields()
        self.set_image(url=None)
        self.title = title
        self.description = description
        self.color = color

        # Author and footer
        if author:
            self.set_author(name=author.name, icon_url=author.icon_url)
        self.set_footer(text=self.FOOTER_TEXT)
        return self
    
    # Function to send an embed
    async def send(self, channel_id: int, view: ui.View = None) -> Message:
        channel = self.bot.get_channel(channel_id)
        self.view = view
        if channel is None:
            raise ValueError("Channel not found")
        message : Message = await channel.send(embed=self, view=self.view)
        self.message_id = message.id
        self.channel_id = channel_id
        return message

    # Function to send to a channel
    async def send_to(self, channel: TextChannel, view: ui.View = None) -> Message:
        self.view = view
        message = await channel.send(embed=self, view=self.view)
        self.message_id = message.id
        self.channel_id = channel.id
        return message
    
    # Function to respond to an interaction with an embed
    async def respond_to(self, interaction: Interaction, view: ui.View = None, ephmeral: bool = False) -> WebhookMessage:
        """
        Respond to an interaction with an embed message

        Parameters
        ----------
        interaction : Interaction
            the interaction to respond to, must be deferred
        view : ui.View
            the view to attach to the message
        ephmeral : bool
            whether the message should be ephmeral or not
        """
        message : WebhookMessage = None
        self.view = view
        if self.view is None:
            message = await interaction.followup.send(embed=self, ephemeral=ephmeral)
        else:
            message = await interaction.followup.send(embed=self, view=self.view, ephemeral=ephmeral)
        self.message_id = message.id
        self.channel_id = interaction.channel_id
        return message

    # Function to update the embeds message
    async def update(self, now: bool = False) -> Message:

        # For updating now
        if now:
            if self.update_task and not self.update_task.done():
                self.update_task.cancel()
            return await self._update(buffer_time=0.0)

        # If a task is set
        if self.update_task and not self.update_task.done():
            return
        
        self.update_task = asyncio.create_task(self._update())
        return await self.update_task
    
    # Internal function to update message
    async def _update(self, buffer_time: float = 0.5) -> None:
        await asyncio.sleep(buffer_time)
        message = await self.get_message()
        return await message.edit(embed=self, view=self.view)

    # Function to delete an embed
    async def delete(self) -> None:
        message = await self.get_message()
        await message.delete()