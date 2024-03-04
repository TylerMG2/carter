from discord import Interaction, Embed, Message, User
from discord.ext import commands
from .panorama import Panorama
import time
import random
from .data import COUNTRIES, PANORAMAS
from enum import Enum

# Strings
CHALLENGE_DESCRIPTION = '''You can make a guess with the `/guess` command.
Googles [Privacy Policy](http://www.google.com/policies/privacy) and [Terms of Sevice](http://www.google.com/intl/en/policies/terms)'''
INVALID_COUNTRY = 'Invalid country guess'
PLAYER_WON_DESCRIPTION = '**{0:}** correctly guessed {1:} :flag_{2:}:\n[**Street View**:link:]({3:})'
TIMES_UP_DESCRIPTION = 'The country was {0:} :flag_{1:}:\n[**Street View**:link:]({2:})'
STREETVIEW_DESCRIPTION = 'Check out the streetview [**here**]({0:}).'

# Status enum
class ChallengeStatus(Enum):
    PENDING = 0
    ACTIVE = 1
    ENDED = 2

class Challenge:

    def __init__(self, author_id: int, time_limit: int = 0):
        self.time_limit : int = time_limit
        self.author_id : int = author_id
        self.guesses = set()
        self.pano : Panorama = None
        self.status : ChallengeStatus = ChallengeStatus.PENDING
        self.winner : User = None

    # Function to pick a random country and panorama
    def pick_random_pano(self) -> Panorama:
        country_iso2 = random.choice(list(COUNTRIES.keys()))
        pano_info = PANORAMAS[PANORAMAS['country'] == country_iso2].sample().iloc[0]
        return Panorama(pano_info['pano_id'], pano_info['lat'], pano_info['long'], pano_info['date'], COUNTRIES[country_iso2], country_iso2)
        
    # Start the challenge
    async def start(self) -> Embed:
        self.status = ChallengeStatus.ACTIVE
        self.pano = self.pick_random_pano()
        return self.to_embed()

    # Make a guess
    async def make_guess(self, guess: str) -> bool:

        # Check if the guess is a valid country
        if (guess not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            raise ValueError(INVALID_COUNTRY)

        # Check if the guess is incorrect
        if (guess != self.pano.iso2) and (guess.lower() != self.pano.country.lower()):
            self.guesses.add(f":flag_{guess.lower()}:")
            return False
        return True

    # End the challenge
    async def end(self, winner: User = None) -> Embed:

        # Check challenge status
        if self.status == ChallengeStatus.ENDED:
            return None
        self.status = ChallengeStatus.ENDED
        self.winner = winner
        return self.to_embed()
    
    # Convert the challenge to an embed
    def to_embed(self) -> Embed:

        # Build embed
        title = 'Country Challenge'
        description = CHALLENGE_DESCRIPTION
        colour = 0x0000ff

        if self.status == ChallengeStatus.ENDED:
            if self.winner:
                description = PLAYER_WON_DESCRIPTION.format(self.winner.mention, self.pano.country, self.pano.iso2.lower(), self.pano.get_streetview_url())
                colour = 0x00ff00
            else:
                description = TIMES_UP_DESCRIPTION.format(self.pano.country, self.pano.iso2.lower(), self.pano.get_streetview_url())
                colour = 0xff0000
        embed = Embed(title=title, description=description, color=colour)

        # Add image
        if self.status == ChallengeStatus.ACTIVE:
            embed.set_image(url=self.pano.get_image_url())
            embed.add_field(name='Guesses', value='\n'.join(self.guesses), inline=False)
        else:
            embed.set_thumbnail(url=self.pano.get_image_url())
            embed.add_field(name='Google Street View', value=STREETVIEW_DESCRIPTION.format(self.pano.get_streetview_url()), inline=False)
        embed.set_footer(text='Bot created by Tyler')
        return embed