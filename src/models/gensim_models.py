from typing import Tuple

import gensim.downloader as gs_api

from codenames_ai import EmbeddingsModel


class GensimModel(EmbeddingsModel):
    def __init__(self, model_name):
        super().__init__()
        self.model = gs_api.load(model_name)

    def find_candidates(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[Tuple[str, float]]:
        return self.model.most_similar(positive=target_cards, negative=avoid_cards, topn=n)

    def guess_word(self, clue: str, words: list[str], n=10) -> list[tuple[str, float]]:
        guess = self.model.most_similar_to_given(clue, words)
        similarity = self.model.similarity(clue, guess)
        return [(guess, similarity)][:n]


class Word2VecModel(GensimModel):
    def __init__(self, model_name="word2vec-google-news-300"):
        super().__init__(model_name)


class FastTextModel(GensimModel):
    def __init__(self, model_name="fasttext-wiki-news-subwords-300"):
        super().__init__(model_name)
