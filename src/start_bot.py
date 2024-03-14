import logging
import os
import sys

import discord
from dotenv import dotenv_values

from ai_players.multi_arm_guesser import MultiArmGuesser
from ai_players.multi_arm_spymaster import MultiArmSpy
from discord_bot.codenames_cog import CodenamesCog
from codenames_engine import Codenames
from models.gensim_models import Word2VecModel, FastTextModel
from models.multi_arm_model import MultiArmModel
from discord.ext import commands


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)


RUN_DIR = os.path.dirname(os.getcwd())
env = dotenv_values(os.path.join(RUN_DIR, '.env'))

# start the game
codenames = Codenames()

# load word embedding models
log.info("loading word2vec...")
#word2vec_engine = Word2VecModel()
log.info("loading fasttext...")
#fasttext_engine = FastTextModel()
#multi_arm_vector_engine = MultiArmModel([word2vec_engine, fasttext_engine])

noop_engine = MultiArmModel([])

# create ai spymaster
spy = MultiArmSpy(codenames, noop_engine)

# create ai guesser
guesser = MultiArmGuesser(codenames, noop_engine)

# setup discord_bot bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    intents=intents,
    command_prefix="!"
)

@bot.event
async def setup_hook() -> None:
    await bot.add_cog(CodenamesCog(bot))


bot.run(env["TOKEN"])

