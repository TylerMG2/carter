from discord import Interaction, Embed, Message, User
from .panorama import Panorama
from .streetview import get_pano_in_country
import pandas as pd
import time

# Load country_data.csv
country_data = pd.read_csv('./resources/country_data.csv')

class Challenge:
    def __init__(self):
        self.guesses = set()
        self.message : Message = None
        self.country : str = ""
        self.pano : Panorama
        self.ended = False

    # Start the challenge
    async def start(self, interaction: Interaction, timer: int = 60):

        # Get a random country
        _, _, self.country = country_data.sample().iloc[0].to_list()
        self.pano = await get_pano_in_country(self.country)

        # Future time
        future_timestamp = int(time.time()) + timer
        
        # Create an embed
        self.embed = Embed(title=f'Country Challenge\n`Ends`<t:{future_timestamp}:R>', description=f'You can make a guess with the `/guess` command.', color=0x0000ff)
        self.embed.set_image(url=self.pano.get_image_url(120))
        self.embed.add_field(name='Guesses', value='', inline=False)
        self.embed.set_footer(text='Bot created by Tyler')

        # Send the embed
        self.message = await interaction.followup.send(embed=self.embed)

    # Make a guess
    async def make_guess(self, interaction: Interaction, guess: str) -> bool:

        # Check if the guess is a valid country
        guess = guess.lower()
        if guess not in country_data['name'].str.lower().values:
            await interaction.response.send_message('Invalid country guess', ephemeral=True, delete_after=5)
            return False

        # Grab the country data
        name, iso2, iso3 = country_data[country_data['name'].str.lower() == guess].iloc[0].to_list()

        # Add to the guesses set
        self.guesses.add(f":flag_{iso2.lower()}:")
        self.embed.set_field_at(0, name='Guesses', value=','.join(self.guesses), inline=False)
        await self.message.edit(embed=self.embed)

        # Check if the guess is correct
        if iso3 == self.country:
            await interaction.response.send_message('Correct!', ephemeral=True, delete_after=5)
            return True
        else:
            await interaction.response.send_message('Incorrect guess', ephemeral=True, delete_after=5)
            return False

    # End the challenge
    async def end(self, winner: User = None):
        
        # Check if the challenge has already ended
        if self.ended:
            return

        self.ended = True

        # Get country info
        name, iso2, _ = country_data[country_data['alpha-3'] == self.country].iloc[0].to_list()
        
        # Build final embed
        end_embed : Embed = None
        if winner:
            end_embed = Embed(title=f'Game Over!', description=f'**{winner.mention}** correctly guessed {name} :flag_{iso2.lower()}:', color=0x00ff00)
            end_embed.set_thumbnail(url=winner.avatar)
        else:
            end_embed = Embed(title=f'Times up!', description=f'The country was {name} :flag_{iso2.lower()}:', color=0xff0000)
            end_embed.set_thumbnail(url=self.pano.get_image_url(120))
        end_embed.set_footer(text="Bot created by Tyler")

        # Update the challenge message
        await self.message.edit(embed=end_embed)