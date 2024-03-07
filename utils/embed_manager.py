from discord import Embed, Message, User
from discord.ext import commands

# This class is used to manage the creation, editing and deletion of embeds
#TODO: Add some errors for when the message_id or channel_id is not set
class EmbedManager:

    """
    A class used to manage a single embed message.
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
    FOOTER_TEST = "Bot by @tmg1"

    # Constructor
    def __init__(self, bot: commands.Bot, embed: Embed=None):
        self.bot = bot
        self.embed = embed
        self.author_id : int = None
        self.message_id : int = None
        self.channel_id : int = None

    # Function to get the embed message
    async def get_message(self) -> Message:
        if self.message_id is None or self.channel_id is None:
            return None
        channel = self.bot.get_channel(self.channel_id)
        return await channel.fetch_message(self.message_id)
    
    # Function to get the author of the embed message
    async def get_author(self) -> User:
        if self.author_id is None:
            return None
        return await self.bot.fetch_user(self.author_id)

    # Function to create an embed
    async def create(self, title: str, description: str, color: int = 0x00ff00, author_id: int = None) -> Embed:
        self.embed = Embed(title=title, description=description, color=color)

        # Set author
        if author_id:
            self.author_id = author_id
            author = await self.get_author()
            self.embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        else:
            self.embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)

        self.embed.set_footer(text=self.FOOTER_TEST)
        return self.embed
    
    # Function to send an embed
    async def send(self, channel_id: int) -> None:
        channel = self.bot.get_channel(channel_id)
        message = await channel.send(embed=self.embed)
        self.message_id = message.id
        self.channel_id = channel_id

    # Function to update an embed
    async def update(self, embed: Embed = None) -> None:
        if embed:
            self.embed = embed
        message = await self.get_message()
        if message:
            await message.edit(embed=self.embed)

    # Function to delete an embed
    async def delete(self) -> None:
        message = await self.get_message()
        if message:
            await message.delete()


class EmbedMessage(Embed):

    def __init__(self, title: str, description: str, color: int = 0x00ff00, author_id: int = None):
        super().__init__(title=title, description=description, color=color)
        self.author_id = author_id
        self.set_footer(text=EmbedManager.FOOTER_TEST)

    async def send(self, channel_id: int, bot: commands.Bot) -> None:
        channel = bot.get_channel(channel_id)
        message = await channel.send(embed=self)
        return message.id

    async def update(self, message_id: int, channel_id: int, bot: commands.Bot) -> None:
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.edit(embed=self)

    async def delete(self, message_id: int, channel_id: int, bot: commands.Bot) -> None:
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.delete()