from discord.ext import commands
from discord import app_commands
from discord import Embed, Interaction
from .streetview import get_pano_in_country

# Geoguessr cog for commands associated with the geoguessr game
class Geoguessr(commands.Cog):

    # Challenges list
    challenges = []

    # Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # Cog Status command
    @commands.command()
    @commands.is_owner()
    async def geostatus(self, ctx: commands.Context):
        await ctx.send('Geoguessr cog is up and running!')
    
    # Challenge slash command
    @app_commands.command(name='challenge', description='Create a new geoguessr challenge')
    async def challenge(self, interaction: Interaction):

        # Deferring the response
        await interaction.response.defer(thinking=True)
        
        # Get a panorama in a random country
        pano = await get_pano_in_country('NDL')

        # Create an embed
        embed = Embed(title='Geoguessr Challenge', description='Can you guess where this is?', color=0x00ff00)
        embed.set_image(url=pano.get_image_url(120))
        embed.add_field(name='Guesses', value='', inline=False)
        embed.set_footer(text="Created by Tyler", icon_url=interaction.user.avatar)

        # Send the embed
        await interaction.followup.send(embed=embed)

# Setup the Geoguessr cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Geoguessr(bot))
    print('Geoguessr cog loaded')