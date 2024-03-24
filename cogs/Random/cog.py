from discord.ext import commands
from discord import Member, VoiceState

OJAS_ID = 226677092530651153
GENERAL_CHANNEL = 951754022849744898
MESSAGES = [
    "Anyone down for among us? Because <@{:0}> just joined <#{:1}>",
    "The overwatch goat is here! <@{:0}> is in <#{:1}> (The party is filling up fast)",
    "Holy Cow! <@{:0}> just joined <#{:1}>, you better get in quick",
    "A shiny <@{:0}> has appeared! Join <#{:1}> for a chance to catch him",
    "CLICK HERE! <@{:0}> is in <#{:1}>",
    "The stars have aligned, <@{:0}> just joined <#{:1}>!",
    "You have to see it too believe it! <@{:0}> is in <#{:1}>",
    "WTF! <@{:0}> just joined <#{:1}>",
    "Am I seeing this right? Is <@{:0}> in <#{:1}>, can someone please check for me.",
    "<@{:0}> has had enough of league, he's in <#{:1}> now",
]

class Random(commands.Cog):

    last_message_index = 0

    # Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # On voice channel join
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if member.id == OJAS_ID and before.channel is None and after.channel is not None:
            message = MESSAGES[self.last_message_index]
            self.last_message_index = (self.last_message_index + 1) % len(MESSAGES)

            # Get the default channel
            channel = member.guild.get_channel(GENERAL_CHANNEL)
            await channel.send(message.format(OJAS_ID, after.channel.id))

async def setup(bot: commands.Bot):
    await bot.add_cog(Random(bot))
    print('Random Cog loaded')