from codenames.models.sbert_model import LLMModel
from codenames_ai import GuesserAI
from codenames_engine import Codenames


class LLMGuesser(GuesserAI):

    def __init__(self, game: Codenames, model: LLMModel):
        super().__init__(game)
        self.model = model

    def find_guess(self, word: str, count: int) -> list[tuple[str, float]]:
        guess = []

        return guess
