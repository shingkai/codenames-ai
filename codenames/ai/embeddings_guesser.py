from codenames.codenames_ai import GuesserAI


class EmbeddingsGuesser(GuesserAI):

    def find_guess(self, word: str, count: int = 3) -> list[tuple[str, float]]:
        words: list[str] = [w.lower() for w in self.game.board.public_unrevealed_words()]
        guess = self.model.find_most_similar_from_list(word.lower(), words, n=count)
        return guess
