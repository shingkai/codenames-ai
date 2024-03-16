from itertools import combinations
from typing import Tuple

from codenames.codenames_ai import SpymasterAI
from codenames.codenames_engine import Team


class EmbeddingsSpy(SpymasterAI):

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
            candidates = self.model.find_centroid_word(list(targets), avoid_cards)
            valid_clues = list(filter(lambda clue: SpymasterAI.is_valid_clue(clue[0], card_words), candidates))
            clues.extend([(result[0], result[1], targets) for result in valid_clues])

        return self.rank_clues(clues)[:n]

    def _initial_clues(self, team: Team, n=3) -> list[Tuple[str, float, list[str]]]:
        pass

    def _pre_guess_clue(self, clue: str, targets: list[str]) -> list[tuple[str, float]]:
        hits = self.model.find_most_similar_from_list(clue, targets, n=3)
        matches = [(hit, score) for (hit, score) in hits if hit in targets]
        return matches