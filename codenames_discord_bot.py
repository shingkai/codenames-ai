from dotenv import dotenv_values
import logging
from typing import Literal
import discord
from discord import app_commands
from codenames_engine import Codenames


# init env vars
config = dotenv_values(".env")

# init logging
log = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode='w')


class CodenamesClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

## only sync when there is an update to the app_command definition, otherwise we may get throttled by discord
#    async def setup_hook(self):
#        await self.tree.sync()

intents = discord.Intents.default()
client = CodenamesClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
        

class SpymasterSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(
            placeholder="Select players to be Spymasters",
        )

    async def callback(self, interaction: discord.Interaction):
        users: List[Union[discord.Member, discord.User]] = self.values
        for user in users:
            dm = await user.create_dm()
            await dm.send("You were selected to be a Spymaster")

        
class SpymasterSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SpymasterSelect())
        

class CardButton(discord.ui.Button):
    def __init__(self, x: int, y: int, word):
        super().__init__(style=discord.ButtonStyle.success, label=word, row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        color = self.view.game.guess(self.label)
        if (color is None):
            return
        if (color == "RED"):
            self.style = discord.ButtonStyle.danger
        if (color == "BLUE"):
            self.style = discord.ButtonStyle.primary
        if (color == "GREY"):
            self.style = discord.ButtonStyle.secondary
        if (color == "BLACK"):
            self.style = discord.ButtonStyle.secondary
        self.disabled = True
        await interaction.response.edit_message(content=self.view.statusMessage(), view=self.view)


class CodenamesView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.game = Codenames()
        cards = self.game.board.public_cards()
        for x in range(5):
            for y in range(5):
                self.add_item(CardButton(x,y, cards[x*5+y][0]))


    def statusMessage(self) -> str:
        winner = self.game.winner()
        message = ""
        if (winner is None):
            message += f"{self.game.turn} turn\n"
            message += f"RED: {self.game.remaining['RED']} | BLUE: {self.game.remaining['BLUE']}"
        else:
            self.disable_board()
            if (self.game.assassinated is not None):
                message += f"{self.game.assassinated} team hit the assassin!\n"
            message += f"{winner} team wins!\n"
        return message

    def disable_board(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


@client.tree.command()
async def codenames(interaction: discord.Interaction):
    """Play a game of Codenames"""
    #interaction.response.send_message(f'Select players to be spymasters', ephemeral=True, view=SpymasterSelectView())
    view = CodenamesView()
    await interaction.response.send_message(content=view.statusMessage(), view=view)
    


client.run(config["TOKEN"])
