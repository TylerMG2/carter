from datetime import datetime
from typing import Any
from discord import Colour, Embed, Message, User
from discord.ext import commands

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
    FOOTER_TEXT = "Bot by @tmg1"

    # Constructor
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.author_id = None
        self.message_id = None
        self.channel_id = None

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
    async def update_author(self, author_id: int) -> None:

        # No author, set bot as the author
        if author_id is None:
            self.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
            return
        
        # Update the author_id and the embed message
        self.author_id = author_id
        author = await self._get_author()
        if not author:
            raise ValueError("Author not found")
        self.set_author(name=author.display_name, icon_url=author.avatar.url)
    
    # Function to reset current embed values and set new valies
    async def update_embed(self, title: str, description: str, color: int = 0x00ff00) -> Embed:
        self.clear_fields()
        self.title = title
        self.description = description
        self.color = color

        # Author and footer
        await self.update_author(self.author_id)
        self.set_footer(text=self.FOOTER_TEXT)
        return self
    
    # Function to send an embed
    async def send(self, channel_id: int) -> Message:
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            raise ValueError("Channel not found")
        message = await channel.send(embed=self)
        self.message_id = message.id
        self.channel_id = channel_id
        return message

    # Function to update the embeds message
    async def update(self) -> None:
        message = await self.get_message()
        await message.edit(embed=self)

    # Function to delete an embed
    async def delete(self) -> None:
        message = await self.get_message()
        await message.delete()