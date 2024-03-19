from abc import ABC, abstractmethod


class CodenamesModel(ABC):
    @abstractmethod
    def find_centroid_word(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[tuple[str, float]]:
        pass

    @abstractmethod
    def find_most_similar_from_list(self, clue: str, words: list[str], n=10) -> list[tuple[str, float]]:
        pass
