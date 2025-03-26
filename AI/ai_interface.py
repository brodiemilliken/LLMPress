from abc import ABC, abstractmethod

class AIPredictorInterface(ABC):
    @abstractmethod
    def predict_next_words(self, text: str, k: int) -> list:
        """
        Predict the top K most likely next words given the input text.

        Args:
            text (str): The input text prompt.
            k (int): Number of top predictions to return.

        Returns:
            list: A list of the top K predicted next words.
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
    def get_word_from_tokens(self, token: int or list) -> str:
        """
        Get the word(s) corresponding to a given token or list of tokens.

        Args:
            token (int or list): The input token ID or list of token IDs.

        Returns:
            str: The decoded word(s) corresponding to the token(s).
        """
        pass