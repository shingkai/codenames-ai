import logging
import os
from typing import Union, Any

import discord
from discord import Interaction
from discord._types import ClientT
from dotenv import dotenv_values

from codenames.codenames_ai import SpymasterAI, GuesserAI
from codenames.codenames_engine import Codenames, Team, CardColor

# init logging
log = logging.getLogger(__name__)
handler = logging.FileHandler(filename='../../discord_bot.log', encoding='utf-8', mode='w')
log.addHandler(handler)

# init env vars
ENV_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config = dotenv_values(os.path.join(ENV_DIR, '.env'))


def color_emoji(color: CardColor) -> str:
    if color == "RED":
        return "🟥"
    if color == "BLUE":
        return "🟦"
    if color == "GREY":
        return "⬜"
    if color == "BLACK":
        return "⬛"


class SpymasterView(discord.ui.View):
    """
    View containing the board with colors revealed (for spymaster eyes only)
    """

    def __init__(self, game: Codenames):
        super().__init__(timeout=None)
        self.game = game
        self.spy_view_dms = []
        cards = self.game.board.hidden_cards()
        for x in range(5):
            for y in range(5):
                self.add_item(CardButton(x, y, cards[x * 5 + y][0], cards[x * 5 + y][1], True))

    async def cross_out_word(self, word: str):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.label == word.upper() or item.label == "🥷 " + word.upper():
                    item.label = '\u0336'.join(item.label) + '\u0336'
        for dm in self.spy_view_dms:
            await dm.edit(content=dm.content, view=self)


class SpymasterSelect(discord.ui.UserSelect):
    """
    Defines a dropdown menu with a list of server members to choose from. Sends a dm to the selected user with the revealed board

    TODO: If the Codenames-AI bot is selected, a codenames AI will generate the clues for its respective team
    """

    def __init__(self, team: Team, ai_spy: SpymasterAI, spy_view: SpymasterView):
        super().__init__(
            placeholder=f"Select {color_emoji(team)} {team} Spymaster...",
        )
        self.team = team
        self.ai_spy = ai_spy
        self.spy_view = spy_view

    async def callback(self, interaction: discord.Interaction):
        users: list[Union[discord.Member, discord.User]] = self.values
        for user in users:
            if user.bot is not True:
                spy_view_dm = await user.create_dm()
                spy_view_dm_msg = await spy_view_dm.send(
                    f"You were selected to be {color_emoji(self.team)} {self.team} Spymaster",
                    view=self.spy_view)
                self.spy_view.spy_view_dms.append(spy_view_dm_msg)
                spy_ai_dm = await user.create_dm()
                await spy_ai_dm.send(f"Need help coming up with a clue? Ask the AI Spymaster",
                                     view=SpyMasterAIView(self.team, self.ai_spy))
            else:
                # TODO: enable spymaster AI if the bot is selected
                return
        if len(users) > 0:
            self.disabled = True
            await interaction.message.delete()


class SpymasterSelectView(discord.ui.View):
    """
    View containing the SpymasterSelect dropdown
    """

    def __init__(self, game: Codenames, spy_view: SpymasterView, team: Team, ai_spy: SpymasterAI):
        super().__init__(timeout=None)
        self.game = game
        self.add_item(SpymasterSelect(team, ai_spy, spy_view))


class SpyMasterAIView(discord.ui.View):
    def __init__(self, team: Team, ai_spy: SpymasterAI):
        super().__init__(timeout=None)
        self.add_item(SpyMasterAIButton(team, ai_spy))


class SpyMasterAIButton(discord.ui.Button):
    def __init__(self, team: Team, ai_spy: SpymasterAI):
        super().__init__(label=f"{color_emoji(team)} Ask AI")
        self.team = team
        self.ai_spy = ai_spy

    async def callback(self, interaction: discord.Interaction):
        log.info(f"{self.team} team asked ai for clue")
        await interaction.response.defer(thinking=True, ephemeral=True)
        log.debug(f"searching for clues...")
        ai_clues = self.ai_spy.find_clue(self.team)
        log.debug(f"{len(ai_clues)} clues generated")
        clue_strings = "\n".join(
            [f"{clue} - {100 * score:.2f}% -> {list(targets)}" for (clue, score, targets) in ai_clues])
        msg = f"{color_emoji(self.team)} AI clue suggestions:```\n{clue_strings}\n```"
        log.debug(msg)
        await interaction.edit_original_response(content=msg)


class GuesserAIModal(discord.ui.Modal, title='AI Guesser'):
    def __init__(self, ai_guesser: GuesserAI):
        super().__init__()
        self.ai_guesser = ai_guesser

    clue = discord.ui.TextInput(
        label=f"Ask AI",
        placeholder="clue word..."
    )

    async def on_submit(self, interaction: discord.Interaction):
        log.info(f"players asked ai for a guess")
        # await interaction.response.defer(thinking=True)
        log.debug(f"searching for guesses for clue {self.clue.value}...")
        ai_guesses = self.ai_guesser.find_guess(self.clue.value.lower())
        log.debug(f"{len(ai_guesses)} guesses generated")
        guess_strings = "\n".join([f"{self.clue.value} -> {guess} {100 * score:.2f}%" for (guess, score) in ai_guesses])
        msg = f"AI guess suggestions:```\n{guess_strings}\n```"
        log.debug(msg)
        await interaction.response.send_message(content=msg, ephemeral=True)


class GuesserAIButton(discord.ui.Button):
    def __init__(self, ai_guesser: GuesserAI):
        super().__init__(label="Ask AI Guesser")
        self.ai_guesser = ai_guesser

    async def callback(self, interaction: Interaction[ClientT]) -> Any:
        await interaction.response.send_modal(GuesserAIModal(self.ai_guesser))


class PassTurnButton(discord.ui.Button):
    """
    Button to allow players to pass the turn to the opposing team
    """

    def __init__(self):
        super().__init__(label="PASS TURN")

    async def callback(self, interaction: discord.Interaction):
        self.view.game.end_turn()
        await interaction.response.edit_message(content=self.view.status_message(), view=self.view)


class GameStatusView(discord.ui.View):
    """
    View containing the status of the game, including which team's turn it is, as well as the number of hidden words remaining for each team.
    Also contains the PassTurnButton, which cannot be in the main PublicBoardView as there is a limit to 25 items per view.
    """

    def __init__(self, game: Codenames, ai_guesser: GuesserAI):
        super().__init__(timeout=None)
        self.game = game
        self.add_item(PassTurnButton())
        self.add_item(GuesserAIButton(ai_guesser))

    def status_message(self) -> str:
        winner = self.game.winner()
        message = ""
        if winner is None:
            message += f"{color_emoji(self.game.turn)} {self.game.turn} turn\n"
            message += f"{color_emoji('RED')} RED: {self.game.remaining['RED']} | {color_emoji('BLUE')} BLUE: {self.game.remaining['BLUE']}"
        else:
            if self.game.assassinated is not None:
                message += f"{color_emoji(self.game.assassinated)} {self.game.assassinated} team hit the 🥷 assassin!\n"
            message += f"{color_emoji(winner)} {winner} team wins!\n"
        return message

    def disable_pass_button(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


class CardButton(discord.ui.Button):
    """
    A button representing a card on the board. May be unrevealed (green colored) or revealed (red, blue, or grey colored and disabled)
    """

    def __init__(self, x: int, y: int, word, color=None, disabled=False):
        super().__init__(style=CardButton.color_to_style(color), label=word, row=y, disabled=disabled)
        self.x = x
        self.y = y
        if color == "BLACK":
            self.label = "🥷 " + word

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        prev_turn = self.view.game.turn
        color = self.view.game.guess(self.label)
        if color is None:
            return
        msg = f"{color_emoji(prev_turn)} {prev_turn} team guessed {self.label}, which was {color_emoji(color)} {color}"
        self.style = CardButton.color_to_style(color)
        self.disabled = True
        # also cross out the corresponding card in the spymaster view
        if isinstance(self.view, PublicBoardView):
            await self.view.spymaster_view.cross_out_word(self.label)
        self.label = '\u0336'.join(self.label) + '\u0336'
        if color == "BLACK":
            self.label = "🥷 " + self.label
        if self.view.game.winner() is not None:
            self.view.disable_board()
            self.view.status_view.disable_pass_button()
        await interaction.response.edit_message(content=msg, view=self.view)
        await self.view.status_message.edit(content=self.view.status_view.status_message(), view=self.view.status_view)

    @staticmethod
    def color_to_style(color) -> discord.ButtonStyle:
        if color == "RED":
            return discord.ButtonStyle.danger
        if color == "BLUE":
            return discord.ButtonStyle.primary
        if color == "GREY":
            return discord.ButtonStyle.secondary
        if color == "BLACK":
            return discord.ButtonStyle.success
        if color is None:
            return discord.ButtonStyle.success


class PublicBoardView(discord.ui.View):
    """
    View containing the board of cards as visible to the public.

    This view has a reference to the GameStatusView and status_message to allow it to update the score and turn as buttons in this view are interacted with
    """

    def __init__(self, game: Codenames, status_view: GameStatusView):
        super().__init__(timeout=None)
        self.status_view = status_view
        self.status_message: discord.WebhookMessage
        self.game = game
        self.spymaster_view = None
        cards = self.game.board.public_cards()
        for x in range(5):
            for y in range(5):
                self.add_item(CardButton(x, y, cards[x * 5 + y][0]))

    def disable_board(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
