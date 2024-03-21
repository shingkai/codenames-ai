import logging
from typing import Optional

import torch
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from sentence_transformers import SentenceTransformer, util
from torch import Tensor

from codenames.models.codenames_model import CodenamesModel

log = logging.getLogger(__name__)


abspath = os.path.abspath(__file__)
pkg_root = os.path.dirname(os.path.dirname(abspath))
env = dotenv_values(os.path.join(pkg_root, '.env'))

CLUE_POOL_FILE = env["CLUE_POOL_FILE"]


class SBertModel(CodenamesModel):
    def __init__(self, model_name):
        super().__init__()
        self.model = SentenceTransformer(model_name)
        self._initialize_embeddings()

    def _get_vector(self, input: str | list[str]) -> Tensor:
        log.debug(f"getting sbert embeddings for {input}")
        vector: Tensor = self.model.encode(input, convert_to_tensor=True)
        return vector

    def _initialize_embeddings(self):
        log.debug(f"loading embeddings...")
        prefix = CLUE_POOL_FILE
        log.debug(f"opening milvus collection: {prefix} ...")
        self.embeddings = EmbeddingsDB(collection_name=prefix)
        if self.embeddings.db.num_entities == 0:
            filename = CLUE_POOL_FILE
            log.debug(f"loading candidate word dictionary from {filename}")
            with open(filename) as f:
                dictionary = f.read().splitlines()
                for word in dictionary:
                    self.embeddings.put([word], [self._get_vector(word)])

    def find_most_similar_from_list(self, clue: str, words: list[str], n=10) -> list[tuple[str, float]]:
        clue_vector = self._get_vector(clue)
        list_vector = self._get_vector(words)
        log.debug(f"getting closest vectors for {clue} among {words}")
        results = util.semantic_search(clue_vector, list_vector, top_k=n)[0]
        guesses = [(words[result['corpus_id']], result['score']) for result in results]
        log.debug(guesses)
        return guesses

    def find_centroid_word(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[tuple[str, float]]:
        log.debug(f"finding centroid of {target_cards} while avoiding {avoid_cards}")
        target_vectors = self._get_vector(target_cards)
        avoid_vectors = self._get_vector(avoid_cards)

        centroid = torch.mean(target_vectors, dim=0)
        result = self.embeddings.search(centroid)
        log.debug(f"search result: {result}")
        return result

    def _distance(self, embedding: Tensor, targets: list[Tensor], avoids: list[Tensor]) -> float:
        pos = 0.0
        neg = 0.0
        for target in targets:
            pos += util.cos_sim(embedding, target).item()
        for avoid in avoids:
            neg += util.cos_sim(embedding, avoid).item()
        return neg - pos


class MiniLMModel(SBertModel):
    def __init__(self):
        super().__init__(model_name="all-MiniLM-L12-v2")


class EmbeddingsDB:
    def __init__(self, collection_name: str, dimension: int = 384):
        connections.connect(host='localhost', port='19530')
        self.db = Collection(name=collection_name,
                             schema=CollectionSchema(fields=[
                                 FieldSchema(
                                     name="word",
                                     dtype=DataType.VARCHAR,
                                     max_length=32,
                                     is_primary=True
                                 ),
                                 FieldSchema(
                                     name="embeddings",
                                     dtype=DataType.FLOAT_VECTOR,
                                     dim=dimension,
                                 )
                             ]))
        log.debug(f"number of entries in embeddings db: {self.db.num_entities}")
        index = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        }
        self.db.create_index("embeddings", index)
        self.db.load()

    def put(self, words: list[str], embeddings: list[Tensor]) -> Optional[str]:
        data = [words, embeddings]
        result = self.db.insert(data)
        log.debug(f"inserted entries: {result.insert_count}")
        log.debug(f"total entries: {self.db.num_entities}")

    def search(self, vector: Tensor, limit: int = 10):
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10},
        }
        result = self.db.search(
            data=[vector.tolist()],
            anns_field="embeddings",
            param=search_params,
            limit=limit)
        log.debug(f"{[(hit.id, hit.distance) for hit in result[0]]}")
        return [(hit.id.lower(), hit.distance) for hit in result[0]]
