from discord import ui, Interaction, SelectOption, ButtonStyle

class BattleRoyaleSettingsView(ui.View):

    def __init__(self):
        super().__init__()
        self.started = None
        self.round_time = 60
        self.lockin_time = 15
        self.lives = 3
        self.powerups = []

    # Guesses select
    @ui.select(placeholder='🎯 Guesses', options=[
        SelectOption(label='1', value=1),
        SelectOption(label='2', value=2),
        SelectOption(label='3', value=3),
        SelectOption(label='4', value=4),
        SelectOption(label='5', value=5),
        ])
    async def guesses_select(self, interaction: Interaction, select: ui.Select):
        self.lives = select.values[0]
        await interaction.response.defer()

    # Time limit select
    @ui.select(placeholder='⏰ Round Time', options=[
        SelectOption(label='15 Seconds', value=15),
        SelectOption(label='30 Seconds', value=30),
        SelectOption(label='1 Minute', value=60),
        SelectOption(label='2 Minutes', value=120),
        SelectOption(label='5 Minutes', value=300),
        SelectOption(label='10 Minutes', value=600),
        ])
    async def round_time_select(self, interaction: Interaction, select: ui.Select):
        self.round_time = select.values[0]
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
    @ui.button(label='Cancel', row=4, style=ButtonStyle.red)
    async def cancel_button(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(content='Battle Royale cancelled.', delete_after=5)
        self.started = False
        self.stop()

    # Stop button
    @ui.button(label='Create', row=4, style=ButtonStyle.green)
    async def create_button(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(content='Creating Battle Royale...', delete_after=5)
        self.started = True
        self.stop()
    
# Lobby view
class BattleRoyaleLobbyView(ui.View):

    def __init__(self, players: dict[int, int], host_id: int, update_players: callable):
        super().__init__()
        self.players = players
        self.host_id = host_id
        self.update_players = update_players

    # Join button
    @ui.button(label='Join', emoji='✅', style=ButtonStyle.green)
    async def join_button(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id not in self.players:
            self.players[interaction.user.id] = 0
            await interaction.response.send_message('You have joined the Battle Royale.', ephemeral=True, delete_after=5)
            await self.update_players()
        else:
            await interaction.response.send_message('You are already in the Battle Royale.', ephemeral=True, delete_after=5)

    # Leave button
    @ui.button(label='Leave', emoji='🚪', style=ButtonStyle.red)
    async def leave_button(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id in self.players:
            self.players.pop(interaction.user.id)
            await interaction.response.send_message('You have left the Battle Royale.', ephemeral=True, delete_after=5)
            await self.update_players()
        else:
            await interaction.response.send_message('You are not in the Battle Royale.', ephemeral=True, delete_after=5)

    @ui.button(label='Settings', emoji='⚙️', style=ButtonStyle.grey)
    async def settings_button(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id == self.host_id:
            await interaction.response.send_message('Settings', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message('Only the host can change the settings.', ephemeral=True, delete_after=5)
        
    # Start button
    @ui.button(label='Start', emoji='➡️', style=ButtonStyle.blurple)
    async def start_button(self, interaction: Interaction, button: ui.Button):
        if interaction.user.id == self.host_id:
            await interaction.response.defer()
            self.stop()
        else:
            await interaction.response.send_message('Only the host can start the game.', ephemeral=True, delete_after=5)