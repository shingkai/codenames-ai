import logging

from codenames.codenames_ai import GuesserAI
from codenames_engine import Codenames
from codenames.models.codenames_model import CodenamesModel

log = logging.getLogger(__name__)


class EmbeddingsGuesser(GuesserAI):

    def __init__(self, game: Codenames, model: CodenamesModel):
        super().__init__(game)
        self.model = model

    def find_guess(self, word: str, count: int = 3) -> list[tuple[str, float]]:
        log.debug(f"looking for guesses based on clue: {word}")
        words: list[str] = [w.lower() for w in self.game.board.public_unrevealed_words()]
        guess = self.model.find_most_similar_from_list(word.lower(), words, n=count)
        return guess
