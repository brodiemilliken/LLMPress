from typing import List, Tuple, Any
import logging

from ..exceptions import TokenizationError
from ..utils.error_handler import with_error_handling

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.Tokenizer')

# Direct API client functions - these are simple pass-throughs
# to maintain backward compatibility

@with_error_handling(
    context="Text tokenization",
    handled_exceptions={
        Exception: TokenizationError
    }
)
def tokenize(text: str, api_client) -> List[Any]:
    """
    Simple pass-through to the API client's tokenize function.

    Args:
        text (str): The input text to tokenize.
        api_client: The API client to use for tokenization.

    Returns:
        List[Any]: A list of tokens.

    Raises:
        TokenizationError: If tokenization fails for any reason
    """
    logger.info(f"Tokenizing text of length {len(text)}")
    result = api_client.tokenize(text)
    logger.info(f"Successfully tokenized text into {len(result)} tokens")
    return result

@with_error_handling(
    context="Multiple text chunks tokenization",
    handled_exceptions={
        Exception: TokenizationError
    }
)
def tokenize_chunks(texts: List[str], api_client, window_size: int = 64) -> List[List[Tuple[str, int]]]:
    """
    Tokenize multiple text chunks using the API client.

    Args:
        texts (List[str]): List of text chunks to tokenize.
        api_client: The API client to use.
        window_size (int): Size of the sliding context window for token prediction.

    Returns:
        List[List[Tuple[str, int]]]: A list of lists of encoded tokens.

    Raises:
        TokenizationError: If tokenization fails for any reason
    """
    logger.info(f"Tokenizing {len(texts)} text chunks with window size {window_size}")
    result = api_client.tokenize_chunks(texts, window_size)
    logger.info(f"Successfully tokenized {len(texts)} chunks")
    return result
