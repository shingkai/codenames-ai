import logging

import discord
from discord import app_commands
from discord.ext import commands

from codenames.ai.embeddings_guesser import EmbeddingsGuesser
from codenames.ai.embeddings_spymaster import EmbeddingsSpy
from codenames.ai.llm_guesser import LLMGuesser
from codenames.app.codenames_discord_bot import GameStatusView, PublicBoardView, SpymasterSelectView, SpymasterView
from codenames.codenames_engine import Codenames
from codenames.models.codenames_model import CodenamesModel
from codenames.models.llm_model import FructoseModel

log = logging.getLogger(__name__)


class CodenamesCog(commands.Cog):
    def __init__(self, client, model: CodenamesModel):
        self.client = client
        self.model = model

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f'Logged in as {self.client.user} (ID: {self.client.user.id})')
        log.info('------')

    @app_commands.command()
    async def codenames(self, interaction: discord.Interaction):
        """Play a game of Codenames"""
        log.info('starting a new game of codenames...')
        game = Codenames()

        log.info('creating ai spy and guesser...')
        ai_guesser = EmbeddingsGuesser(game, self.model)
        ai_spy = EmbeddingsSpy(game, self.model, ai_guesser)

        status_view = GameStatusView(game, ai_guesser)
        public_view = PublicBoardView(game, status_view)

        await interaction.response.send_message(content=None, view=public_view)
        public_view.status_message = await interaction.followup.send(content=status_view.status_message(),
                                                                     view=status_view,
                                                                     wait=True)

        spymaster_view = SpymasterView(game)

        red_spy_select_view = SpymasterSelectView(game, spymaster_view, "RED", ai_spy)
        await interaction.followup.send(content=f'Select player to be RED Spymaster (AI players not yet enabled)',
                                        ephemeral=False, view=red_spy_select_view)
        blue_spy_select_view = SpymasterSelectView(game, spymaster_view, "BLUE", ai_spy)
        await interaction.followup.send(content=f'Select player to be BLUE Spymaster (AI players not yet enabled)',
                                        ephemeral=False, view=blue_spy_select_view)

        public_view.spymaster_view = spymaster_view
