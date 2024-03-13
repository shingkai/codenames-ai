import re
from abc import ABC, abstractmethod
from typing import Tuple

from gensim.models import KeyedVectors

from codenames_engine import Codenames, Team


class InferenceEngine(ABC):
    def __init__(self):
        self.engine: KeyedVectors

    @abstractmethod
    def find_candidates(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[Tuple[str, float]]:
        pass


class SpymasterAI(ABC):
    """
    An AI Spymaster player.
    """
    def __init__(self, game: Codenames, engine: InferenceEngine):
        self.game = game
        self.model = engine

    @abstractmethod
    def find_clue(self, team: Team, n=3) -> list[Tuple[str, int]]:
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


class GuesserAI:
    def __init__(self, game: Codenames, ie: InferenceEngine):
        self.game = game
        self.ie = ie
