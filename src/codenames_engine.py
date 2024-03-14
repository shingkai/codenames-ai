import os
from dotenv import dotenv_values
import logging
from typing import Literal, Optional, Tuple
import random

log = logging.getLogger(__name__)

PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
env = dotenv_values(os.path.join(PARENT_DIR, '.env'))

WORD_POOL_FILE = env["WORD_POOL_FILE"]

Team = Literal["RED", "BLUE"]
CardColor = Literal["RED", "BLUE", "GREY", "BLACK"]


class Codenames:
    def __init__(self):
        self.board = Board()
        self.turn: Team = "RED"
        self.remaining = {"RED": 9, "BLUE": 8}
        self.assassinated: Optional[Team] = None

    def public_words(self) -> list[str]:
        return [word for (word, revealed) in self.board.public_cards() if revealed is None]

    def winner(self) -> Optional[Team]:
        if self.assassinated is not None:
            return Codenames.opposite_team(self.assassinated)
        if self.remaining["RED"] == 0:
            return "RED"
        if self.remaining["BLUE"] == 0:
            return "BLUE"
        return None

    def end_turn(self) -> Team:
        self.turn = Codenames.opposite_team(self.turn)
        return self.turn

    def guess(self, word) -> Optional[CardColor]:
        if self.winner() is not None:
            log.info(f"The game is over, {self.winner()} team has won the game!")
            log.info(self.remaining)
            return None
        card = self.board.reveal(word)
        if card is None:
            log.warning(f"Invalid guess: {word} is not an unrevealed card on the board")
            return None
        if card.color == "BLACK":
            self.assassinated = self.turn
            return card.color
        if card.color == "GREY":
            self.end_turn()
            return card.color
        if card.color == self.turn:
            self.remaining[self.turn] -= 1
        else:
            self.remaining[Codenames.opposite_team(self.turn)] -= 1
            self.end_turn()
        return card.color

    @staticmethod
    def opposite_team(color: Literal["RED", "BLUE"]) -> Literal["RED", "BLUE"]:
        if color == "RED":
            return "BLUE"
        if color == "BLUE":
            return "RED"


class Card:
    def __init__(self, word: str, color: CardColor, revealed: Optional[CardColor] = None):
        self.word = word
        self.color = color
        self.revealed = revealed

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.word} ({self.color}, revealed={self.revealed})"

    def reveal(self):
        self.revealed = self.color


class Board:
    def __init__(self, word_file=WORD_POOL_FILE):
        with open(word_file) as f:
            word_pool = f.read().splitlines()
        self.words = random.sample(word_pool, k=25)

        self.red = [Card(word, "RED") for word in self.words[0:9]]
        self.blue = [Card(word, "BLUE") for word in self.words[9:17]]
        self.grey = [Card(word, "GREY") for word in self.words[17:24]]
        self.black = [Card(word, "BLACK") for word in self.words[24:]]

        self.cards = self.red + self.blue + self.grey + self.black
        random.shuffle(self.cards)

    def public_cards(self) -> list[Tuple[str, Optional[CardColor]]]:
        return [(card.word, card.revealed) for card in self.cards]

    def hidden_cards(self) -> list[Tuple[str, CardColor, Optional[CardColor]]]:
        return [(card.word, card.color, card.revealed) for card in self.cards]

    def reveal(self, word) -> Optional[Card]:
        for card in self.cards:
            if card.word == word and card.revealed is None:
                card.reveal()
                return card
        return None
