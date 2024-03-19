from abc import ABC, abstractmethod
import logging

from fructose import Fructose
from openai import OpenAI

from codenames.models.codenames_model import CodenamesModel

log = logging.getLogger(__name__)

class LLMModel(ABC):
    @abstractmethod
    def find_clue(self, words: list[str]) -> str:
        pass

    @abstractmethod
    def guess_clue(self, clue: str, words: list[str]) -> str:
        pass


class FructoseModel(CodenamesModel):

    # def __init__(self, model_name: str):
    #     client = OpenAI(
    #         api_key='ollama',
    #         base_url="http://127.0.0.1:11434/v1/"
    #         )
    #     self.ai = Fructose(client = client, model=model_name)


    client = OpenAI(api_key='ollama', base_url="http://127.0.0.1:11434/v1/")
    ai = Fructose(client = client, model='gemma:2b-instruct')
    
    @ai
    def find_clue(words: list[str]) -> str:
        """
        Given a list of words, find one other word that is related to them all.
        """
        ...

    @ai
    def guess_clue(clue: str, words: list[str]) -> str:
        """
        Given a clue, find the best word from the list of words that is most related to the clue.
        """
        ...

    def find_centroid_word(self, target_cards: list[str], avoid_cards: list[str], n=10) -> list[tuple[str, float]]:        
        return [(FructoseModel.find_clue(target_cards), 1.0)]

    def find_most_similar_from_list(self, clue: str, words: list[str], n=10) -> list[tuple[str, float]]:
        log.debug(f"find_most_similar_from_list({clue}, {words})")
        return [(FructoseModel.guess_clue(clue, words), 1.0)]


