from typing import Tuple

from src.codenames_ai import EmbeddingsModel


class MultiArmModel(EmbeddingsModel):

    def __init__(self, models: list[EmbeddingsModel]):
        super().__init__()
        self.models = models

    def find_candidates(self, targets: list[str], avoids: list[str], n=10) -> list[Tuple[str, float]]:
        candidates = []
        for child_model in self.models:
            candidates.extend(child_model.find_candidates(targets, avoids, n))
        return sorted(candidates, key=lambda x: x[1], reverse=True)[:n]

    def guess_word(self, clue: str, words: list[str], n=10) -> list[tuple[str, float]]:
        guesses = []
        for child_model in self.models:
            guesses.extend(child_model.guess_word(clue, words))
        return sorted(guesses, key=lambda x: x[1], reverse=True)[:n]
