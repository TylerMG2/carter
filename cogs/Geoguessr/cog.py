from discord.ext import commands
from discord import app_commands

# Geoguessr cog for commands associated with the geoguessr game
class Geoguessr(commands.Cog):

    # Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # Cog Status command
    @commands.command()
    @commands.is_owner()
    async def geostatus(self, ctx: commands.Context):
        await ctx.send('Geoguessr cog is up and running!')
    
    # Challenge slash command

# Setup the Geoguessr cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Geoguessr(bot))
    print('Geoguessr cog loaded')