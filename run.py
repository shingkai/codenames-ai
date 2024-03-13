import sys

sys.path.append('src')

import logging

from src.ai_players.multi_arm_spymaster import MultiArmSpy
from src.codenames_engine import Codenames
from src.engines.multi_arm_engine import MultiArmEngine
from src.engines.vector_engine import Word2VecEngine, FastTextEngine

log = logging.getLogger('codenames_ai')

codenames = Codenames()
log.info("loading word2vec...")
word2vec_engine = Word2VecEngine()
log.info("loading fasttext...")
fasttext_engine = FastTextEngine()
multi_arm_vector_engine = MultiArmEngine([word2vec_engine, fasttext_engine])
ai = MultiArmSpy(codenames, multi_arm_vector_engine)
log.info("finding clues")
ai_clues = ai.find_clue("RED", n=10)
print(ai_clues)
