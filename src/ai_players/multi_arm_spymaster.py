from itertools import combinations
from typing import Tuple

from codenames_ai import SpymasterAI
from codenames_engine import Team


class MultiArmSpy(SpymasterAI):

    def find_clue(self, team: Team, n=3) -> list[Tuple[str, float, list[str]]]:
        cards = self.game.board.hidden_cards()
        card_words = [word.lower() for (word, color, revealed) in cards]
        remaining_cards = list(filter(lambda x: x[2] is None, cards))
        target_cards = [word.lower() for (word, color, revealed) in remaining_cards if color == team]
        avoid_cards = [word.lower() for (word, color, revealed) in remaining_cards if color == 'BLACK']

        target_groups = []
        for k in range(1, 4):
            target_groups.extend(combinations(target_cards, k))

        clues: list[Tuple[str, float, list[str]]] = []
        for targets in target_groups:
            candidates = self.model.find_candidates(list(targets), avoid_cards)
            valid_clues = list(filter(lambda clue: SpymasterAI.is_valid_clue(clue[0], card_words), candidates))
            clues.extend([(result[0], result[1], targets) for result in valid_clues])

        return self.rank_clues(clues)[:n]

    @staticmethod
    def weighted_score(score: int, count: int) -> float:
        return score * (1 + 0.1 * count)

    @staticmethod
    def rank_clues(clues: list[Tuple[str, float, list[str]]]) -> list[Tuple[str, float, list[str]]]:
        weighted_clues = [(word, MultiArmSpy.weighted_score(score, len(targets)), targets) for (word, score, targets) in
                          clues]
        return sorted(weighted_clues, key=lambda x: x[1], reverse=True)
