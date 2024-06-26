from discord.ext import commands
from discord import app_commands, Interaction
from .challenge import Challenge
from .battleroyale import BattleRoyaleLobby
from .data import COUNTRIES
import asyncio
import typing

MAX_TIME_LIMIT = 600 # 10 minutes

# Geoguessr cog for commands associated with the geoguessr game
class Geoguessr(commands.Cog):

    # Challenges list
    challenges : dict[int, Challenge] = {}
    battle_royales : dict[int, BattleRoyaleLobby] = {}

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
        await interaction.response.defer(thinking=True)

        # Check if the time limit is too large
        if timer > MAX_TIME_LIMIT:
            await interaction.response.send_message(f'Time limit must be less then {MAX_TIME_LIMIT} seconds.', ephemeral=True)
            return

        # If there is already a challenge in the channel, delete it
        if interaction.channel_id in self.challenges:
            old_challenge = self.challenges.pop(interaction.channel_id)
            await old_challenge.end()
            
        # Add the challenge to the challenges list
        new_challenge = Challenge(self.bot, interaction)
        await new_challenge.start(timeout=timer)
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
        if interaction.channel_id not in self.challenges and interaction.channel_id not in self.battle_royales:
            await interaction.response.send_message('No active challenge exists in this channel, start one with /challenge', ephemeral=True, delete_after=5)
            return
        
        # If there is a battle royale, add the guess to the battle royale
        if interaction.channel_id in self.battle_royales:
            battle_royale = self.battle_royales[interaction.channel_id]
            try:
                await battle_royale.add_guess(interaction, country)
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True, delete_after=5)
            return
        
        # Add the guess to the challenge
        challenge = self.challenges[interaction.channel_id]
        try:
            correct = await challenge.add_guess(interaction, country)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True, delete_after=5)
            return

        # If the result is true, remove the challenge
        if correct:
            self.challenges.pop(interaction.channel_id)

    # Battle royale create command
    @app_commands.command(name='battleroyale', description='Create a new geoguessr battle royale lobby')
    async def battle_royale(self, interaction: Interaction):
        
        # TODO: Handle battle royale already in progress

        # Create new battle royale
        await interaction.response.defer()
        lobby = BattleRoyaleLobby(self.bot)
        await lobby.create_lobby(interaction, lobby_suffix="Battle Royale", thread=True)
        self.battle_royales[lobby.thread_id] = lobby

# Setup the Geoguessr cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Geoguessr(bot))
    print('Geoguessr Cog loaded')