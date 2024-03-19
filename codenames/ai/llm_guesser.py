import logging
from codenames.codenames_ai import GuesserAI
from codenames.models.codenames_model import CodenamesModel
from codenames_engine import Codenames
from models.llm_model import LLMModel

log = logging.getLogger(__name__)

class LLMGuesser(GuesserAI):

    def __init__(self, game: Codenames, model: CodenamesModel):
        super().__init__(game)
        self.model = model

    def find_guess(self, word: str, count: int=3) -> list[tuple[str, float]]:
        remaining_words = [w.lower() for w in self.game.board.public_unrevealed_words()]
        guesses = []
        for i in range(count):
            guesses = self.model.find_most_similar_from_list(word.lower(), remaining_words)
            log.debug(f"clue {word.lower()} -> {guesses}")
            remaining_words.remove(guesses[0].lower())
            guesses.append((guesses, 1.0))

        return guesses
