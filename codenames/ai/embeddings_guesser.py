from codenames.codenames_ai import GuesserAI


class EmbeddingsGuesser(GuesserAI):

    def find_guess(self, word: str) -> list[tuple[str, float]]:
        words: list[str] = [w.lower() for w in self.game.public_words()]
        guess = self.model.find_most_similar_from_list(word, words)
        return guess
