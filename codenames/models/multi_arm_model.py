from typing import Tuple

from codenames.codenames_ai import EmbeddingsModel


class MultiArmModel(EmbeddingsModel):

    def __init__(self, models: list[EmbeddingsModel]):
        super().__init__()
        self.models = models

    def find_centroid_word(self, targets: list[str], avoids: list[str], n=10) -> list[Tuple[str, float]]:
        candidates = []
        for child_model in self.models:
            candidates.extend(child_model.find_centroid_word(targets, avoids, n))
        return sorted(candidates, key=lambda x: x[1], reverse=True)[:n]

    def find_most_similar_from_list(self, clue: str, words: list[str], n=10) -> list[tuple[str, float]]:
        guesses = []
        for child_model in self.models:
            guesses.extend(child_model.find_most_similar_from_list(clue, words))
        return sorted(guesses, key=lambda x: x[1], reverse=True)[:n]
