from discord import Message, User, Interaction
from discord.ext import commands
from .panorama import Panorama
from utils.embed_message import EmbedMessage
import time
import random
from .data import COUNTRIES, get_random_pano

# Strings
CHALLENGE_IN_PROGRESS_COLOR = 0x0000ff
CHALLENGE_ENDED_COLOR = 0xff0000
CHALLENGE_WON_COLOR = 0x00ff00
CHALLENGE_TITLE = ":map: Country Challenge"
CHALLENGE_DESCRIPTION = """You can make a guess with the `/guess` command.
Googles [Privacy Policy](http://www.google.com/policies/privacy) and [Terms of Sevice](http://www.google.com/intl/en/policies/terms)"""
PLAYER_WON_DESCRIPTION = "**{0:}** correctly guessed **{1:} :flag_{2:}:**"
TIMES_UP_TITLE = ":alarm_clock: Time's Up!"
TIMES_UP_DESCRIPTION = "The country was **{0:} :flag_{1:}:**"
STREETVIEW_TITLE = "\n\n:blue_car: [**Streetview**]({0:})"
INCORRECT_MESSAGES = [
    "Incorrect.",
    "Nope.",
    "Try again.",
    "Not quite.",
    "Wrong.",
    "Nearly (This means absolutely nothing)"
]

CORRECT_MESSAGES = [
    "Correct!",
    "Nice one!",
    "You got it!",
    "Well done!",
]

class Challenge:

    def __init__(self, bot: commands.Bot, interaction: Interaction):
        self.embed_message = EmbedMessage(bot)
        self.interaction = interaction    
        self.guesses = set()
        self.pano : Panorama = None
        self.ended = False
        
    # Start the challenge
    async def start(self, timeout: int = 0) -> Message:
        self.pano = get_random_pano()

        # Create timer string
        timer = ""
        if timeout > 0:
            future_time = int(time.time() + timeout)
            timer = f"`Ends`<t:{future_time}:R>\n"

        # Update the embed message
        self.embed_message.update_embed(description=timer+CHALLENGE_DESCRIPTION, color=CHALLENGE_IN_PROGRESS_COLOR)
        self.embed_message.add_field(name='Guesses', value='No guesses yet', inline=False)
        self.embed_message.set_image(url=self.pano.get_image_url())
        self.embed_message.set_author(name=f"{self.interaction.user.display_name}'s Challenge", icon_url=self.interaction.user.display_avatar.url)
        
        # Respond to the interaction
        return await self.embed_message.respond(self.interaction)
        
    # Make a guess
    async def add_guess(self, interaction: Interaction, guess: str) -> bool:
        guess = guess.lower()

        # Check if the guess is a valid country
        if (guess.upper() not in COUNTRIES.keys()) and (guess not in COUNTRIES.values()):
            raise ValueError(f"Invalid country guess: {guess}")
        
        # Check if the guess is correct
        if guess == self.pano.iso2.lower() or guess == self.pano.country.lower():
            await interaction.response.send_message(f'{random.choice(CORRECT_MESSAGES)}', ephemeral=True, delete_after=5)
            await self.end(winner=interaction.user)
            return True
        
        # Build guess flags
        self.guesses.add(guess)
        guess_flags = [f":flag_{guess}:" for guess in self.guesses]
        self.embed_message.set_field_at(0, name='Guesses', value='  '.join(guess_flags), inline=False)
        await self.embed_message.update()
        await interaction.response.send_message(f'{random.choice(INCORRECT_MESSAGES)}', ephemeral=True, delete_after=5)
        return False
    
    # End the challenge
    async def end(self, winner: User = None) -> Message:

        # Make sure the challange hasn't ended
        if self.ended:
            return
        self.ended = True

        streetview_link = STREETVIEW_TITLE.format(self.pano.get_streetview_url())

        # Pick end screen
        if winner:
            self.embed_message.update_embed(description=PLAYER_WON_DESCRIPTION.format(winner.mention, self.pano.country, self.pano.iso2.lower()) + streetview_link, 
                                            color=CHALLENGE_WON_COLOR)
            self.embed_message.set_author(name=f"{winner.display_name} guessed the country!", icon_url=winner.display_avatar.url)
        else:
            self.embed_message.remove_author()
            self.embed_message.update_embed(title=TIMES_UP_TITLE,
                                            description=TIMES_UP_DESCRIPTION.format(self.pano.country, self.pano.iso2.lower()) + streetview_link, 
                                            color=CHALLENGE_ENDED_COLOR)

        # Google streetview link
        self.embed_message.set_thumbnail(url=self.pano.get_image_url())
        return await self.embed_message.update()
        

    
    
