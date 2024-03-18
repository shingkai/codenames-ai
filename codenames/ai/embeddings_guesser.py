from codenames.codenames_ai import GuesserAI
from codenames_engine import Codenames
from models.embeddings_model import EmbeddingsModel


class EmbeddingsGuesser(GuesserAI):

    def __init__(self, game: Codenames, model: EmbeddingsModel):
        super().__init__(game)
        self.model = model

    def find_guess(self, word: str, count: int = 3) -> list[tuple[str, float]]:
        words: list[str] = [w.lower() for w in self.game.board.public_unrevealed_words()]
        guess = self.model.find_most_similar_from_list(word.lower(), words, n=count)
        return guess
