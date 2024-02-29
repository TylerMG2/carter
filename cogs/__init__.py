from discord.ext.commands import Bot

# Import cog classes
from .Geoguessr.cog import Geoguessr

# Function to add cogs
async def setup_cogs(bot: Bot):
    await bot.add_cog(Geoguessr(bot))
    print('Geoguessr cog loaded')