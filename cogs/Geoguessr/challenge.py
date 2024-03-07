from discord import Interaction, Embed, Message, User
from discord.ext import commands
from .panorama import Panorama
from ...utils.embed_manager import EmbedManager
import time
import random
from .data import COUNTRIES, PANORAMAS
from enum import Enum

# Strings
CHALLENGE_IN_PROGRESS_COLOR = 0x0000ff
CHALLENGE_ENDED_COLOR = 0xff0000
CHALLENGE_WON_COLOR = 0x00ff00
CHALLENGE_TITLE = "Country Challenge"
CHALLENGE_WINNER_TITLE = "Winner"
CHALLENGE_DESCRIPTION = """You can make a guess with the `/guess` command.
Googles [Privacy Policy](http://www.google.com/policies/privacy) and [Terms of Sevice](http://www.google.com/intl/en/policies/terms)"""
PLAYER_WON_DESCRIPTION = "**{0:}** correctly guessed {1:} :flag_{2:}:"
TIMES_UP_DESCRIPTION = "The country was {0:} :flag_{1:}:\n[**Street View**:link:]({2:})"
STREETVIEW_DESCRIPTION = "Check out the streetview [**here**]({0:})."

class Challenge:

    def __init__(self, author_id: int):
        self.author_id = author_id
        self.embed_manager = EmbedManager()
        self.guesses = set()
        self.pano : Panorama = None

    # Function to pick a random country and panorama
    def pick_random_pano(self) -> Panorama:
        country_iso2 = random.choice(list(COUNTRIES.keys()))
        pano_info = PANORAMAS[PANORAMAS['country'] == country_iso2].sample().iloc[0]
        return Panorama(pano_info['pano_id'], pano_info['lat'], pano_info['long'], pano_info['date'], COUNTRIES[country_iso2], country_iso2)
        
    # Start the challenge
    async def start(self, timeout: int = 0) -> Embed:
        self.pano = self.pick_random_pano()
        timer = ""
        if timeout > 0:
            future_time = int(time.time() + timeout)
            timer = f"\n'Ends'<t:{future_time}:R>"
        await self.embed_manager.create(CHALLENGE_TITLE+timer, CHALLENGE_DESCRIPTION, CHALLENGE_IN_PROGRESS_COLOR)
        self.embed_manager.embed.set_image(url=self.pano.get_image_url())
        self.embed_manager.embed.add_field(name='Guesses', value='No guesses yet', inline=False)
        

    # Make a guess
    async def make_guess(self, guess: str) -> Embed:

        # Check if the guess is a valid country
        if (guess not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            raise ValueError(f"Invalid country guess: {guess}")
        
        # Add the guess to the set
        self.guesses.add(guess)
        self.embed.set_field_at(0, name='Guesses', value='\n'.join(self.guesses), inline=False)
        return self.embed

    # Set challenge winner
    async def set_winner(self, winner: User) -> Embed:
        self.embed.remove_field(0)
        self.embed.set_thumbnail(url=winner.avatar.url)

        return self.embed    

    
    
