import logging
import sys

from ai_players.multi_arm_guesser import MultiArmGuesser
from ai_players.multi_arm_spymaster import MultiArmSpy
from codenames_engine import Codenames
from models.gensim_models import Word2VecModel, FastTextModel
from models.multi_arm_model import MultiArmModel

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

# start the game
codenames = Codenames()

# load word embedding models
log.info("loading word2vec...")
word2vec_engine = Word2VecModel()
log.info("loading fasttext...")
fasttext_engine = FastTextModel()
multi_arm_vector_engine = MultiArmModel([word2vec_engine, fasttext_engine])

# create ai spymaster
spy = MultiArmSpy(codenames, multi_arm_vector_engine)

# create ai guesser
guesser = MultiArmGuesser(codenames, multi_arm_vector_engine)

# begin playing
# find clues
log.info("finding clues")
ai_clues = spy.find_clue("RED", n=10)
log.info(ai_clues)
clue = ai_clues[0][0]
targets = ai_clues[0][2]
log.info(f"giving clue: '{clue} {len(targets)}'")

# find guesses
log.info(f"finding guesses")
ai_guess = guesser.find_guess(clue)
log.info(ai_guess)

# make a guess and update the game state
guess = ai_guess[0][0]  # guess the first result
log.info(f"guessing {guess}")
codenames.guess(guess.upper())
