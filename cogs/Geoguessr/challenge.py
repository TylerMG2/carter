from discord import Interaction, Embed, Message, User
from discord.ext import commands
from .panorama import Panorama
import asyncio
import time
import random
from .data import COUNTRIES, PANORAMAS

class Challenge:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guesses = set()
        self.channel_id : int = None
        self.message_id : int = None
        self.pano : Panorama = None
        self.timer : asyncio.Task = None

    # Function to wait a specified amount of time before ending the challenge
    async def wait_for_end(self, time_limit: int):
        await asyncio.sleep(time_limit)
        await self.end()
    
    # Get the challenge message
    async def get_message(self) -> Message:
        return await self.bot.get_channel(self.channel_id).fetch_message(self.message_id)

    # Start the challenge
    async def start(self, interaction: Interaction, time_limit: int = 0):

        # Pick a random country and panorama
        country_iso2 = random.choice(list(COUNTRIES.keys()))
        print(country_iso2, COUNTRIES[country_iso2])
        pano_info = PANORAMAS[PANORAMAS['country'] == country_iso2].sample().iloc[0]
        self.pano = Panorama(pano_info['pano_id'], pano_info['lat'], pano_info['long'], pano_info['date'], COUNTRIES[country_iso2], country_iso2)

        # Future time
        title = f'Country Challenge'
        if time_limit > 0:
            future_timestamp = int(time.time()) + time_limit
            title += f'\n`Ends`<t:{future_timestamp}:R>'
        
        # Create an embed
        self.embed = Embed(title=title, description=f'You can make a guess with the `/guess` command.\nGoogles [Privacy Policy](http://www.google.com/policies/privacy) and [Terms of Sevice](http://www.google.com/intl/en/policies/terms)', color=0x0000ff)
        self.embed.set_image(url=self.pano.get_image_url())
        self.embed.add_field(name='Guesses', value='', inline=False)
        self.embed.set_footer(text='Bot created by Tyler')

        # Send the embed
        message = await interaction.followup.send(embed=self.embed)
        self.channel_id = interaction.channel_id
        self.message_id = message.id

        # Start the timer
        if time_limit > 0:
            self.timer = asyncio.create_task(self.wait_for_end(time_limit))

    # Make a guess
    async def make_guess(self, interaction: Interaction, guess: str):

        # Check if the guess is a valid country
        if (guess not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            await interaction.response.send_message('Invalid country guess', ephemeral=True, delete_after=5)
            return

        # Check if the guess is correct
        if (guess != self.pano.iso2) and (guess.lower() != self.pano.country.lower()):
            await interaction.response.send_message('Incorrect guess', ephemeral=True, delete_after=5)

            # Add to the guesses set
            self.guesses.add(f":flag_{guess.lower()}:")
            self.embed.set_field_at(0, name='Guesses', value=','.join(self.guesses), inline=False)
            message = await self.get_message()
            await message.edit(embed=self.embed)
            return
        
        # If the guess is correct, end the challenge
        await interaction.response.send_message('Correct!', ephemeral=True, delete_after=5)
        await self.end(interaction.user)

    # End the challenge
    async def end(self, winner: User = None):
        
        # Build final embed
        end_embed : Embed = None
        if winner:
            end_embed = Embed(title=f'Game Over!', 
                              description=f'**{winner.mention}** correctly guessed {self.pano.country} :flag_{self.pano.iso2.lower()}:\n[**Street View**:link:]({self.pano.get_streetview_url()})', 
                              color=0x00ff00)
            end_embed.set_thumbnail(url=winner.avatar)
        else:
            end_embed = Embed(title=f'Times up!', 
                              description=f'The country was {self.pano.country} :flag_{self.pano.iso2.lower()}:\n[**Street View**:link:]({self.pano.get_streetview_url()})', 
                              color=0xff0000)
            end_embed.set_thumbnail(url=self.pano.get_image_url())
        end_embed.set_footer(text="Bot created by Tyler.")

        # Update the challenge message
        message = await self.get_message()
        await message.edit(embed=end_embed)

        # Cancel the timer
        if self.timer:
            self.timer.cancel()