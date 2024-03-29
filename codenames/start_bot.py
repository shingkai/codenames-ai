import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import dotenv_values

from app.codenames_cog import CodenamesCog
from models.llm_model import FructoseModel
from models.sbert_model import MiniLMModel

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

abspath = os.path.abspath(__file__)
pkg_root = os.path.dirname(os.path.dirname(abspath))
os.chdir(pkg_root)
env = dotenv_values(os.path.join(pkg_root, '.env'))

# load word embedding models
# log.info("loading word2vec...")
# word2vec_engine = Word2VecModel()
# log.info("loading fasttext...")
# fasttext_engine = FastTextModel()

# multi_arm_vector_engine = MultiArmModel([word2vec_engine, fasttext_engine])
# noop_model = MultiArmModel([])

# model = noop_model
model = MiniLMModel()
# model = fasttext_engine
# model = multi_arm_vector_engine
# model = FructoseModel()

# setup discord bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    intents=intents,
    command_prefix="!"
)


@bot.event
async def setup_hook() -> None:
    await bot.add_cog(CodenamesCog(bot, model))


bot.run(env["TOKEN"])
