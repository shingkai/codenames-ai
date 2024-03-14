import logging

import discord
from discord.ext import commands
from discord import app_commands

from codenames_engine import Codenames
from discord_bot.codenames_discord_bot import GameStatusView, PublicBoardView, SpymasterSelectView

log = logging.getLogger(__name__)


class CodenamesCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f'Logged in as {self.client.user} (ID: {self.client.user.id})')
        log.info('------')

    @app_commands.command()
    async def codenames(self, interaction: discord.Interaction):
        """Play a game of Codenames"""
        log.info('starting a new game of codenames')
        game = Codenames()
        status_view = GameStatusView(game)
        public_view = PublicBoardView(game, status_view)

        await interaction.response.send_message(content=None, view=public_view)
        public_view.status_message = await interaction.followup.send(content=status_view.status_message(),
                                                                     view=status_view,
                                                                     wait=True)

        await interaction.followup.send(content=f'Select player to be RED Spymaster (AI players not yet enabled)',
                                        ephemeral=False, view=SpymasterSelectView(game, "RED"))
        await interaction.followup.send(content=f'Select player to be BLUE Spymaster (AI players not yet enabled)',
                                        ephemeral=False, view=SpymasterSelectView(game, "BLUE"))

