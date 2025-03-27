from abc import ABC, abstractmethod
from typing import Union, List

class AI(ABC):
    @abstractmethod
    def list_rank_tokens(self, tokens: list, k: int) -> list:
        """
        Predict the top K most likely next tokens given the input token sequence.
        
        Args:
            tokens (list): The input token sequence
            k (int): Number of top predictions to return
            
        Returns:
            list: Top K token IDs sorted by probability
        """
        pass

    @abstractmethod
    def get_tokens_for_word(self, word: str) -> list:
        """
        Get the token(s) corresponding to a given word.

        Args:
            word (str): The input word to tokenize.

        Returns:
            list: A list of token IDs corresponding to the word.
        """
        pass

    @abstractmethod
    def get_word_from_tokens(self, token: Union[int, List[int]]) -> str:
        """
        Get the word(s) corresponding to a given token or list of tokens.

        Args:
            token (int or list): The input token ID or list of token IDs.

        Returns:
            str: The decoded word(s) corresponding to the token(s).
        """
        pass
        
    @abstractmethod
    def tokenize(self, text: str) -> list:
        """
        Convert a text string into a list of token IDs.

        Args:
            text (str): The input text to tokenize.

        Returns:
            list: A list of token IDs corresponding to the text.
        """
        pass

    @abstractmethod
    def detokenize(self, tokens: list[int]) -> str:
        """
        Convert a list of token IDs into a text string

        Args:
            tokens (list[int]): The input list of token IDs.

        Returns:
            str: The decoded text string corresponding to the token IDs.
        """
        pass