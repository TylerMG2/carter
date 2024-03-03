from discord.ext import commands
from discord import app_commands, Interaction
from .challenge import Challenge
from .data import COUNTRIES
import asyncio
import typing

# Geoguessr cog for commands associated with the geoguessr game
class Geoguessr(commands.Cog):

    # Challenges list
    challenges : dict[int, Challenge] = {}

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
    async def challenge(self, interaction: Interaction, timer: int = 0):

        # Deferring the response
        await interaction.response.defer(thinking=True)

        # If there is already a challenge in the channel, delete it
        if interaction.channel_id in self.challenges:
            old_challenge = self.challenges.pop(interaction.channel_id)
            await old_challenge.end()
            
        # Add the challenge to the challenges list
        new_challenge = Challenge()
        await new_challenge.start(interaction, time_limit=timer)
        self.challenges[interaction.channel_id] = new_challenge

    # Autocomplete for the guess command
    async def guess_autocomplete(self, _: Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        options : typing.List[app_commands.Choice[str]] = []
        for iso2, name in COUNTRIES.items():
            if name.lower().startswith(current.lower()):
                options.append(app_commands.Choice(name=name, value=iso2))
        
        # Only return first 25 options
        return options[:25]  
    
    # Guess slash command
    @app_commands.command(name='guess', description='Guess the location of the geoguessr challenge')
    @app_commands.autocomplete(country=guess_autocomplete)
    async def guess(self, interaction: Interaction, country: str):

        # Check if the challenge exists
        if interaction.channel_id not in self.challenges:
            await interaction.response.send_message('No active challenge exists in this channel, start one with /challenge', ephemeral=True, delete_after=5)
            return
        
        # Add the guess to the challenge
        challenge = self.challenges[interaction.channel_id]
        result = await challenge.make_guess(interaction, country)

        # If the result is true, end the challenge
        if result:
            await challenge.end(interaction.user)
            if interaction.channel_id in self.challenges:
                self.challenges.pop(interaction.channel_id)


# Setup the Geoguessr cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Geoguessr(bot))
    print('Geoguessr cog loaded')