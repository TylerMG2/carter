from discord.ext import commands
from discord import app_commands, Interaction
from .challenge import Challenge
import asyncio

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
            self.challenges.pop(interaction.channel_id)
            await self.challenges[interaction.channel_id].end()
            
        # Add the challenge to the challenges list
        new_challenge = Challenge()
        await new_challenge.start(interaction, timer=timer)
        self.challenges[interaction.channel_id] = new_challenge

        # Wait for the challenge to end
        if timer > 0:
            await asyncio.sleep(timer)

            # End the challenge
            if not new_challenge.ended:
                self.challenges.pop(interaction.channel_id)
                await new_challenge.end()     
    
    # Guess slash command
    @app_commands.command(name='guess', description='Guess the location of the geoguessr challenge')
    async def guess(self, interaction: Interaction, guess: str):

        # Check if the challenge exists
        if interaction.channel_id not in self.challenges:
            await interaction.response.send_message('No active challenge exists in this channel, start one with /challenge', ephemeral=True, delete_after=5)
            return
        
        # Add the guess to the challenge
        challenge = self.challenges[interaction.channel_id]
        result = await challenge.make_guess(interaction, guess)

        # If the result is true, end the challenge
        if result:
            await challenge.end(interaction.user)
            if interaction.channel_id in self.challenges:
                self.challenges.pop(interaction.channel_id)

# Setup the Geoguessr cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Geoguessr(bot))
    print('Geoguessr cog loaded')