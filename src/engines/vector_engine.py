import gensim.downloader as gs_api
from typing import Tuple

from src.codenames_ai import InferenceEngine


class Word2VecEngine(InferenceEngine):
    def __init__(self, model="word2vec-google-news-300"):
        super().__init__()
        self.engine = gs_api.load(model)

    def find_candidates(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[Tuple[str, float]]:
        return self.engine.most_similar(positive=target_cards, negative=avoid_cards, topn=n)


class FastTextEngine(InferenceEngine):
    def __init__(self, model="fasttext-wiki-news-subwords-300"):
        super().__init__()
        self.engine = gs_api.load(model)

    def find_candidates(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[Tuple[str, float]]:
        return self.engine.most_similar(positive=target_cards, negative=avoid_cards, topn=n)
