import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import Guild, Interaction
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup intents
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    # Set status
    await bot.change_presence(activity=discord.Game(name="/battleroyale"))

    # Load cogs
    for folder in os.listdir('./cogs'):
        if os.path.isdir(f'./cogs/{folder}') and not folder.startswith('_'):
            await bot.load_extension(f'cogs.{folder}.cog')
    
    # Sync commands
    if os.getenv("ENV") == "production":
        await sync_commands()

# Ping command
@bot.tree.command(name='ping', description='Replies with Pong!')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong!')

# Sync slash command
async def sync_commands(guild: Guild = None):

    # If guild was supplied, copy global commands to guild
    if guild is not None:
        bot.tree.copy_global_to(guild=guild)
        commands = await bot.tree.sync(guild=guild)
        print(f"Synced {len(commands)} commands to {guild.name}")
    else:
        commands = await bot.tree.sync()
        print(f"Synced {len(commands)} commands")

# Normal command to sync slash commands to current guild
@bot.command()
@commands.is_owner()
async def sync(ctx: Context):
    if os.getenv("ENV") == "development":
        await sync_commands(guild=ctx.guild)
        await ctx.send('Synced commands to this server!')

# If name is main, run the bot
if __name__ == '__main__':
    bot.run(os.getenv('BOT_TOKEN'))