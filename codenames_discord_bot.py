from dotenv import dotenv_values
from typing import Literal
import discord
from discord import app_commands

#init env vars
config = dotenv_values(".env")
secrets = dotenv_values(".env.secret")

#MY_GUILD = discord.Object(id=1212588464571158598)

class CodenamesClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
 #       self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync()

intents = discord.Intents.default()
client = CodenamesClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    
    
@client.tree.command()
@app_commands.describe(
    red_spymaster='The Red Team Spymaster',
    blue_spymaster='The Blue Team Spymaster')
async def codenames(interaction: discord.Interaction,
                    red_spymaster: Literal['Human', 'AI'],
                    blue_spymaster: Literal['Human', 'AI']):
    """Play a game of Codenames"""
    await interaction.response.send_message(f'Starting a game with {red_spymaster} Red spymaster and {blue_spymaster} Blue spymaster')


client.run(secrets["TOKEN"])
