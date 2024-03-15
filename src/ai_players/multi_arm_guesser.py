from codenames_ai import GuesserAI


class MultiArmGuesser(GuesserAI):

    def find_guess(self, word: str) -> list[tuple[str, float]]:
        words: list[str] = [w.lower() for w in self.game.public_words()]
        guess = self.model.guess_word(word, words)
        return guess
