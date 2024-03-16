import os

import discord
from discord.ext import commands
from dotenv import dotenv_values

from app.codenames_cog import CodenamesCog

RUN_DIR = os.path.dirname(os.path.dirname(os.getcwd()))
env = dotenv_values(os.path.join(RUN_DIR, '.env'))

bot = commands.Bot(
    intents=discord.Intents.default(),
    command_prefix="!"
)


@bot.event
async def setup_hook() -> None:
    await bot.add_cog(CodenamesCog(bot))
    await bot.tree.sync()


bot.run(env["TOKEN"])
