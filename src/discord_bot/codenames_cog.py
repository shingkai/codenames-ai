import logging

import discord
from discord import app_commands
from discord.ext import commands

from ai_players import MultiArmSpy, MultiArmGuesser
from codenames_ai import EmbeddingsModel
from codenames_engine import Codenames
from discord_bot.codenames_discord_bot import GameStatusView, PublicBoardView, SpymasterSelectView

log = logging.getLogger(__name__)


class CodenamesCog(commands.Cog):
    def __init__(self, client, model: EmbeddingsModel):
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
        ai_spy = MultiArmSpy(game, self.model)
        ai_guesser = MultiArmGuesser(game, self.model)

        status_view = GameStatusView(game, ai_guesser)
        public_view = PublicBoardView(game, status_view)

        await interaction.response.send_message(content=None, view=public_view)
        public_view.status_message = await interaction.followup.send(content=status_view.status_message(),
                                                                     view=status_view,
                                                                     wait=True)

        await interaction.followup.send(content=f'Select player to be RED Spymaster (AI players not yet enabled)',
                                        ephemeral=False, view=SpymasterSelectView(game, "RED", ai_spy))
        await interaction.followup.send(content=f'Select player to be BLUE Spymaster (AI players not yet enabled)',
                                        ephemeral=False, view=SpymasterSelectView(game, "BLUE", ai_spy))
