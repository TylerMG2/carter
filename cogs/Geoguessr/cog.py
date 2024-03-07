from discord.ext import commands
from discord import app_commands, Interaction
from .challenge import Challenge
from .data import COUNTRIES
import asyncio
import typing

MAX_TIME_LIMIT = 600 # 10 minutes

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

        # Check if the time limit is too large
        if timer > MAX_TIME_LIMIT:
            await interaction.response.send_message(f'Time limit must be less then {MAX_TIME_LIMIT} seconds.', ephemeral=True)
            return

        # If there is already a challenge in the channel, delete it
        if interaction.channel_id in self.challenges:
            old_challenge = self.challenges.pop(interaction.channel_id)
            await old_challenge.end()
            
        # Add the challenge to the challenges list
        new_challenge = Challenge(self.bot, interaction.user.id)
        await new_challenge.start(interaction, time_limit=timer)
        self.challenges[interaction.channel_id] = new_challenge

        # Start timer
        if timer > 0:
            await asyncio.sleep(timer)
            if interaction.channel_id in self.challenges:
                await new_challenge.end()

    # Autocomplete for the guess command
    async def guess_autocomplete(self, _: Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        options : typing.List[app_commands.Choice[str]] = []
        for iso2, name in COUNTRIES.items():
            if name.lower().startswith(current.lower()):

                flag_emoji = ''.join([chr(0x1F1E6 + ord(char) - ord('A')) for char in iso2.upper()])
                options.append(app_commands.Choice(name=f'{flag_emoji} {name}', value=iso2))

        if current == '':
            return options[:1]
        
        # Only return first 5 options
        return options[:5]  
    
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
        correct = await challenge.add_guess(interaction, country)

        # If the result is true, end the challenge
        if correct:
            await challenge.end(winner=interaction.user)
            if interaction.channel_id in self.challenges:
                self.challenges.pop(interaction.channel_id)


# Setup the Geoguessr cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Geoguessr(bot))
    print('Geoguessr cog loaded')