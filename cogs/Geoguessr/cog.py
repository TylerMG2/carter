from discord.ext import commands

# Geoguessr cog for commands associated with the geoguessr game
class Geoguessr(commands.Cog):

    # Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # Status command
    @commands.command()
    async def geostatus(self, ctx: commands.Context):
        await ctx.send('Geoguessr cog is up and running!')

