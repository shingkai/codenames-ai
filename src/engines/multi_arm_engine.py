from typing import Tuple

from src.codenames_ai import InferenceEngine


class MultiArmEngine(InferenceEngine):
    def __init__(self, engines: list[InferenceEngine]):
        super().__init__()
        self.engines = engines

    def find_candidates(self, targets: list[str], avoids: list[str], n=10) -> list[Tuple[str, float]]:
        candidates = []
        for child_engine in self.engines:
            candidates.extend(child_engine.find_candidates(targets, avoids, n))
        return sorted(candidates, key=lambda x: x[1], reverse=True)[:n]
