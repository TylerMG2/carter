from discord import ui
from discord import SelectOption
from discord import Interaction
from discord import ButtonStyle

class BattleRoyaleSettingsView(ui.View):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.time_limit = 60
        self.lockin_time = 5
        self.powerups = []

    # Time limit select
    @ui.select(placeholder='⏰ Time Limit', options=[
        SelectOption(label='15 Seconds', value=15),
        SelectOption(label='30 Seconds', value=30),
        SelectOption(label='1 Minute', value=60),
        SelectOption(label='2 Minutes', value=120),
        SelectOption(label='5 Minutes', value=300),
        SelectOption(label='10 Minutes', value=600),
        ])
    async def time_limit_select(self, interaction: Interaction, select: ui.Select):
        self.time_limit = select.values[0]
        await interaction.response.defer()

    # Lockin time select
    @ui.select(placeholder='🔒 Lockin Time', options=[
        SelectOption(label='No Time', value=0),
        SelectOption(label='5 Seconds', value=5),
        SelectOption(label='10 Seconds', value=10),
        SelectOption(label='15 Seconds', value=15),
        SelectOption(label='30 Seconds', value=30),
        ])
    async def lockin_time_select(self, interaction: Interaction, select: ui.Select):
        self.lockin_time = select.values[0]
        await interaction.response.defer()

    # Powerups select
    @ui.select(placeholder='⚡ Powerups', min_values=0, max_values=3, options=[
        SelectOption(label='50/50', emoji='🎲', value='fifty_fifty'),
        SelectOption(label='Ask ChatGPT', emoji='🤖', value='ask_chatgpt'),
        SelectOption(label='Another Perspective', emoji='📷', value='another_perspective'),
        ])
    async def powerups_select(self, interaction: Interaction, select: ui.Select):
        self.powerups = select.values
        await interaction.response.defer()
    
    # Start button
    @ui.button(label='Cancel', row=3, style=ButtonStyle.red)
    async def cancel_button(self, interaction: Interaction, button: ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message('Battle Royale cancelled', ephemeral=True)

    # Stop button
    @ui.button(label='Create', row=3, style=ButtonStyle.green)
    async def create_button(self, interaction: Interaction, button: ui.Button):
        #await interaction.message.delete()
        await self.game.create(interaction) # Tell the battle royale game to create the game

    
    