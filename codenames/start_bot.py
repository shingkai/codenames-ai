import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import dotenv_values

from app.codenames_cog import CodenamesCog
from models.gensim_models import Word2VecModel, FastTextModel
from models.multi_arm_model import MultiArmModel

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

abspath = os.path.abspath(__file__)
pkg_root = os.path.dirname(os.path.dirname(abspath))
os.chdir(pkg_root)
env = dotenv_values(os.path.join(pkg_root, '.env'))

# load word embedding models
log.info("loading word2vec...")
word2vec_engine = Word2VecModel()
log.info("loading fasttext...")
fasttext_engine = FastTextModel()

multi_arm_vector_engine = MultiArmModel([word2vec_engine, fasttext_engine])
# noop_model = MultiArmModel([])

# model = fasttext_engine
model = multi_arm_vector_engine
# model = noop_model

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
