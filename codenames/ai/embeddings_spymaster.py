import logging
from itertools import combinations

from codenames.codenames_ai import SpymasterAI, GuesserAI
from codenames.codenames_engine import Team, Codenames
from codenames.models.codenames_model import CodenamesModel

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class EmbeddingsSpy(SpymasterAI):
    def __init__(self, game: Codenames, model: CodenamesModel, ai_guesser: GuesserAI):
        super().__init__(game)
        self.model = model
        self.ai_guesser = ai_guesser

    def find_clue(self, team: Team, n: int = 3) -> list[tuple[str, int, float, list[str]]]:
        log.info(f"finding clues for {team} team")
        initial_clues = self._initial_clues(team, 20)
        clue_string = '\n'.join(f"{clue[0]} -> {clue[2]} ({100 * clue[1]:.2f})" for clue in initial_clues)
        log.debug(f"initial candidate clues:\n{clue_string}")
        scored_clues: list[tuple[str, int, float, list[str]]] = []
        public_words = self.game.board.public_unrevealed_words()
        guessed = []
        for (clue, score, targets) in initial_clues:
            if clue in guessed:
                continue
            guessed.append(clue)
            guesses = self._pre_guess_clue(clue, public_words, targets, n)
            (count, score, hits) = self._score_guesses(team, guesses, threshold=0.3)
            scored_clues.append((clue, count, score, hits))

        return sorted(scored_clues, key=lambda x: x[2], reverse=True)[:n]

    def _initial_clues(self, team: Team, n: int = 10) -> list[tuple[str, float, list[str]]]:
        cards = self.game.board.hidden_cards()
        card_words = [word.lower() for (word, color, revealed) in cards]
        remaining_cards = list(filter(lambda x: x[2] is None, cards))
        target_cards = [word.lower() for (word, color, revealed) in remaining_cards if color == team]
        avoid_cards = [word.lower() for (word, color, revealed) in remaining_cards if color == 'BLACK']

        target_groups = []
        for k in range(1, 4):
            target_groups.extend(combinations(target_cards, k))

        clues: list[tuple[str, float, list[str]]] = []
        for targets in target_groups:
            candidates = self.model.find_centroid_word(list(targets), avoid_cards, n=n)
            valid_clues = list(filter(lambda clue: SpymasterAI.is_valid_clue(clue[0], card_words), candidates))
            clues.extend([(result[0], result[1], targets) for result in valid_clues])

        return self.rank_clues(clues)[:n]

    def _pre_guess_clue(self, clue: str, words: list[str], targets: list[str], n: int = 3) -> list[tuple[str, float]]:
        log.debug(f"evaluating candidate clue: {clue} for targets: {targets} among word set: {words}")
        try:
            hits = self.model.find_most_similar_from_list(clue.lower(), [word.lower() for word in words], n)
            # matches = [(hit, score) for (hit, score) in hits if hit in word_set]
            # return sorted(hits, key=lambda x: x[1], reverse=True)
            log.debug(f"pre-guessing results: {hits}")
            return hits
        except KeyError as e:
            log.warning(f"error while finding most similar: {e}")
            return []

    def _score_guesses(self, team: Team, guesses: list[tuple[str, float]], threshold: float = 0.5) -> tuple[
        int, float, list[str]]:
        count = 0
        score = 0.0
        hits = []
        for (guess, weight) in guesses:
            log.debug(f"testing guess: {guess} ({weight})")
            if self.game.board.get_word_color(guess.upper()) == team:
                log.debug(f"{guess} was matching color {self.game.board.get_word_color(guess.upper())}")
                if weight > threshold:
                    score += weight
                    count += 1
                    hits.append(guess)
                else:
                    log.debug(f"confidence: {weight:2f} was too low, skipping")
            else:
                log.debug(f"{guess} was non-matching color {self.game.board.get_word_color(guess.upper())}")
                log.debug(f"first {count} guesses ({hits}) correct, expected score: {score}")
                return count, score, hits
        log.debug(f"first {count} guesses ({hits}) correct, expected score: {score}")
        return count, score, hits
