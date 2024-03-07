from discord import Message, User
from discord.ext import commands
from .panorama import Panorama
from utils.embed_manager import EmbedMessage
import time
import random
from .data import COUNTRIES, PANORAMAS

# Strings
CHALLENGE_IN_PROGRESS_COLOR = 0x0000ff
CHALLENGE_ENDED_COLOR = 0xff0000
CHALLENGE_WON_COLOR = 0x00ff00
CHALLENGE_TITLE = ":map: Country Challenge"
CHALLENGE_WINNER_TITLE = "Winner"
CHALLENGE_DESCRIPTION = """You can make a guess with the `/guess` command.
Googles [Privacy Policy](http://www.google.com/policies/privacy) and [Terms of Sevice](http://www.google.com/intl/en/policies/terms)"""
PLAYER_WON_DESCRIPTION = "**{0:}** correctly guessed {1:} :flag_{2:}:"
TIMES_UP_DESCRIPTION = "The country was {0:} :flag_{1:}:\n[**Street View**:link:]({2:})"
STREETVIEW_DESCRIPTION = "Check out the streetview [**here**]({0:})."

class Challenge:

    def __init__(self, bot: commands.Bot, author_id: int):
        self.embed_message = EmbedMessage(bot)
        self.embed_message.update_author(author_id)
        self.guesses = set()
        self.pano : Panorama = None
        self.ended = False

    # Function to pick a random country and panorama
    def pick_random_pano(self) -> Panorama:
        country_iso2 = random.choice(list(COUNTRIES.keys()))
        pano_info = PANORAMAS[PANORAMAS['country'] == country_iso2].sample().iloc[0]
        return Panorama(pano_info['pano_id'], pano_info['lat'], pano_info['long'], pano_info['date'], COUNTRIES[country_iso2], country_iso2)
        
    # Start the challenge
    async def start(self, channel_id: int, timeout: int = 0) -> Message:
        self.pano = self.pick_random_pano()

        # Create timer string
        timer = ""
        if timeout > 0:
            future_time = int(time.time() + timeout)
            timer = f"\n'Ends'<t:{future_time}:R>"

        # Update the embed message
        await self.embed_message.update_embed(CHALLENGE_TITLE+timer, CHALLENGE_DESCRIPTION, color=CHALLENGE_IN_PROGRESS_COLOR)
        await self.embed_message.add_field(name='Guesses', value='No guesses yet', inline=False)
        await self.embed_message.set_image(self.pano.get_streetview_url())
        return await self.embed_message.send(channel_id)
        
    # Make a guess
    async def add_guess(self, guess: str) -> bool:

        # Check if the guess is a valid country
        if (guess not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            raise ValueError(f"Invalid country guess: {guess}")
        
        # Check if the guess is correct
        if guess.lower() == self.pano.iso2.lower() or guess.lower() == self.pano.country.lower():
            return True
        
        # Build guess flags
        self.guesses.add(guess)
        guess_flags = [f":flag_{guess.lower()}" for guess in self.guesses]
        self.embed_message.set_field_at(0, name='Guesses', value='  '.join(guess_flags), inline=False)
        await self.embed_message.update()
        return False
    
    # End the challenge
    async def end(self, winner: User = None) -> Message:

        # Make sure the challange hasn't ended
        if self.ended:
            return
        self.ended = True

        # Pick end screen
        if winner:
            await self.embed_message.update_embed(CHALLENGE_WINNER_TITLE, 
                                              PLAYER_WON_DESCRIPTION.format(winner.display_name, self.pano.country, self.pano.iso2.lower()), 
                                              color=CHALLENGE_WON_COLOR)
        else:
            await self.embed_message.update_embed(CHALLENGE_TITLE, 
                                              TIMES_UP_DESCRIPTION.format(self.pano.country, self.pano.iso2.lower(), self.pano.get_streetview_url()), 
                                              color=CHALLENGE_ENDED_COLOR)

        # Google streetview link
        await self.embed_message.add_field(name=':blue_car: Street View', value=STREETVIEW_DESCRIPTION.format(self.pano.get_streetview_url()), inline=False)
        return await self.embed_message.update()
        

    
    
