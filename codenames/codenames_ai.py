import re
from abc import ABC, abstractmethod

from codenames_engine import Codenames, Team


class SpymasterAI(ABC):
    """
    An AI Spymaster player.
    """

    def __init__(self, game: Codenames):
        self.game = game

    @abstractmethod
    def find_clue(self, team: Team, n=3) -> list[tuple[str, int, float, list[str]]]:
        pass

    @staticmethod
    def is_valid_clue(clue: str, board: list[str]) -> bool:
        # clue can only contain lowercase letters, filters out special-char gibberish and capitalized/proper nouns
        if re.compile(r'[^a-z]').search(clue):
            return False
        # clues cannot contain any board-word or vice-versa
        for word in board:
            if clue in word or word in clue:
                return False
        return True

    @staticmethod
    def weighted_score(score: int, count: int) -> float:
        return score * (1 + 0.0 * count)

    @staticmethod
    def rank_clues(clues: list[tuple[str, float, list[str]]]) -> list[tuple[str, float, list[str]]]:
        weighted_clues = [(word, SpymasterAI.weighted_score(score, len(targets)), targets) for (word, score, targets) in
                          clues]
        return sorted(weighted_clues, key=lambda x: x[1], reverse=True)


class GuesserAI:
    def __init__(self, game: Codenames):
        self.game = game

    @abstractmethod
    def find_guess(self, word: str, count: int) -> list[tuple[str, float]]:
        pass
