from dotenv import dotenv_values
import logging
from typing import Literal
import discord
from discord import app_commands
from codenames_engine import Codenames, Team



class SpymasterSelect(discord.ui.UserSelect):
    """
    Defines a dropdown menu with a list of server members to choose from. Sends a dm to the selected user with the revealed board

    TODO: If the Codenames-AI bot is selected, a codenames AI will generate the clues for its respective team
    """
    def __init__(self, team: Team):
        super().__init__(
            placeholder=f"Select {team} Spymaster...",
        )
        self.team = team

    async def callback(self, interaction: discord.Interaction):
        users: List[Union[discord.Member, discord.User]] = self.values
        for user in users:
            if (user.bot is not True):
                dm = await user.create_dm()
                await dm.send(f"You were selected to be {self.team} Spymaster", view=SpymasterView(self.view.game))
            else:
                # TODO: enable spymaster AI if the bot is selected
                return
        if (len(users) > 0):
            self.disabled = True
            await interaction.message.delete()



class SpymasterSelectView(discord.ui.View):
    """
    View containing the SpymasterSelect dropdown
    """
    def __init__(self, game: Codenames, team: Team):
        super().__init__()
        self.game = game
        self.add_item(SpymasterSelect(team))


        
class SpymasterView(discord.ui.View):
    """
    View containing the board with colors revealed (for spymaster eyes only)
    """
    def __init__(self, game: Codenames):
        super().__init__()
        self.game = game
        cards = self.game.board.hidden_cards()
        for x in range(5):
            for y in range(5):
                self.add_item(CardButton(x, y, cards[x*5+y][0], cards[x*5+y][1], True))



class PassTurnButton(discord.ui.Button):
    """
    Button to allow players to pass the turn to the opposing team
    """
    def __init__(self):
        super().__init__(label="PASS TURN")

    async def callback(self, interaction: discord.Interaction):
        self.view.game.end_turn()
        await interaction.response.edit_message(content=self.view.status_message() , view=self.view)


        
class GameStatusView(discord.ui.View):
    """
    View containing the status of the game, including which team's turn it is, as well as the number of hidden words remaining for each team.
    Also contains the PassTurnButton, which cannot be in the main PublicBoardView as there is a limit to 25 items per view.
    """
    def __init__(self, game: Codenames):
        super().__init__()
        self.game = game
        self.add_item(PassTurnButton())
    
    def status_message(self) -> str:
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

                

class CardButton(discord.ui.Button):
    """
    A button representing a card on the board. May be unrevealed (green colored) or revealed (red, blue, or grey colored and disabled)
    """
    def __init__(self, x: int, y: int, word, color=None, disabled=False): 
        super().__init__(style=CardButton.color_to_style(color), label=word, row=y, disabled=disabled)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        color = self.view.game.guess(self.label)
        if (color is None):
            return
        self.style = CardButton.color_to_style(color)
        self.disabled = True
        await interaction.response.edit_message(content=f"{self.view.game.turn} team guessed {self.label}, which was {color}", view=self.view)
        await self.view.status_message.edit(content=self.view.status_view.status_message(), view=self.view.status_view)

    @staticmethod
    def color_to_style(color) -> discord.ButtonStyle:
        if (color == "RED"):
            return discord.ButtonStyle.danger
        if (color == "BLUE"):
            return discord.ButtonStyle.primary
        if (color == "GREY"):
            return discord.ButtonStyle.secondary
        if (color == "BLACK"):
            return discord.ButtonStyle.secondary
        if (color is None):
            return discord.ButtonStyle.success

        

class PublicBoardView(discord.ui.View):
    """
    View containing the board of cards as visible to the public.

    This view has a reference to the GameStatusView and status_message to allow it to update the score and turn as buttons in this view are interacted with
    """
    def __init__(self, game: Codenames, status_view: GameStatusView):
        super().__init__()
        self.status_view = status_view
        self.status_message: discord.WebhookMessage = None
        self.game = game
        cards = self.game.board.public_cards()
        for x in range(5):
            for y in range(5):
                self.add_item(CardButton(x,y, cards[x*5+y][0]))

    def disable_board(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True



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

                
@client.tree.command()
async def codenames(interaction: discord.Interaction):
    """Play a game of Codenames"""
    game = Codenames()
    status_view = GameStatusView(game)
    public_view = PublicBoardView(game, status_view)

    await interaction.response.send_message(content=None, view=public_view)
    public_view.status_message = await interaction.followup.send(content=status_view.status_message(), view=status_view, wait=True)

    await interaction.followup.send(content=f'Select player to be RED Spymaster', ephemeral=False, view=SpymasterSelectView(game, "RED"))
    await interaction.followup.send(content=f'Select player to be BLUE Spymaster', ephemeral=False, view=SpymasterSelectView(game, "BLUE"))


client.run(config["TOKEN"])
