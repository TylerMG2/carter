from discord import Embed, User
from .panorama import Panorama
import time



# Functions for generating embeds for different game states
def challenge_embed(pano_url: str, author: User, time_limit: int = 0) -> Embed:

    # Append timer to title
    timer = ""
    if time_limit > 0:
        future_time = int(time.time() + time_limit)
        timer = f"\n'Ends'<t:{future_time}:R>"

    # Create embed
    embed = Embed(title=CHALLENGE_TITLE+timer, description=CHALLENGE_DESCRIPTION, color=CHALLENGE_IN_PROGRESS_COLOR)
    embed.set_image(url=pano_url)
    embed.add_field(name='Guesses', value='No guesses yet', inline=False)
    embed.set_footer(text="Bot by @tmg1")
    embed.set_author(name=author.display_name, icon_url=author.avatar.url)
    return embed

def challenge_timeout_embed(pano: Panorama) -> Embed:
    return Embed(title=CHALLENGE_TITLE, 
                 description=TIMES_UP_DESCRIPTION.format(pano.country, pano.iso2.lower(), pano.get_streetview_url()), 
                 color=CHALLENGE_ENDED_COLOR)