import copy

import gensim.downloader as gs_api

from codenames.codenames_ai import EmbeddingsModel


class GensimModel(EmbeddingsModel):
    def __init__(self, model_name):
        super().__init__()
        self.model = gs_api.load(model_name)

    def find_centroid_word(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[tuple[str, float]]:
        return self.model.most_similar(positive=target_cards, negative=avoid_cards, topn=n)

    def find_most_similar_from_list(self, clue: str, words: list[str], n=3) -> list[tuple[str, float]]:
        guesses: list[tuple[str, float]] = []
        remaining_words = copy.deepcopy(words)
        for i in range(n):
            guess = self.model.most_similar_to_given(clue, remaining_words)
            similarity = self.model.similarity(clue, guess)
            guesses.append((guess, similarity))
            remaining_words.remove(guess)
        return guesses


class Word2VecModel(GensimModel):
    def __init__(self, model_name="word2vec-google-news-300"):
        super().__init__(model_name)


class FastTextModel(GensimModel):
    def __init__(self, model_name="fasttext-wiki-news-subwords-300"):
        super().__init__(model_name)
