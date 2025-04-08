"""
LLMPress Core Decompression Functionality

This module handles the decompression of binary data back to text.
"""
import os
import logging
from typing import Optional, Tuple, List, Any

# Import from within the decompression package
from .detokenizer import detokenize
from .decoder import decode_bytes
from ..exceptions import FileOperationError, DecompressionError, DecodingError, TokenizationError
from ..utils.error_handler import handle_operation_errors, operation_context

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.Decompressor')

def split_tokens_by_breaks(tokens: List[Tuple[str, int]]) -> List[List[Tuple[str, int]]]:
    """
    Split a list of tokens into chunks at <BREAK> tokens.

    Args:
        tokens: List of token tuples

    Returns:
        List of token chunk lists
    """
    if not tokens:
        return []

    # Find indices of all break tokens
    break_indices = [i for i, token in enumerate(tokens) if token[0] == "<BREAK>"]

    # If no breaks found, return the whole token list as a single chunk
    if not break_indices:
        return [tokens]

    # Split the token list at break points
    chunks = []
    start_idx = 0

    for break_idx in break_indices:
        # Add chunk up to (but not including) the break token
        chunks.append(tokens[start_idx:break_idx])
        # Set start of next chunk to after the break token
        start_idx = break_idx + 1

    # Add the final chunk after the last break
    if start_idx < len(tokens):
        chunks.append(tokens[start_idx:])

    return chunks

@handle_operation_errors(
    operation_name="Decompression",
    specific_exceptions={
        FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
        PermissionError: (FileOperationError, "Permission denied: {error_message}"),
        DecodingError: (DecodingError, "Error during binary decoding: {error_message}"),
        TokenizationError: (TokenizationError, "Error during detokenization: {error_message}")
    },
    fallback_exception=DecompressionError
)
def decompress(input_data, model, output_path=None) -> Tuple[str, List[Any]]:
    """
    Decompress binary data or a compressed file.

    Args:
        input_data (bytes or str): Binary data or path to compressed file
        model: The language model to use for detokenization
        output_path (str, optional): Path to save decompressed text

    Returns:
        tuple: (decompressed_text, decoded_tokens)

    Raises:
        FileOperationError: If there's an error reading or writing files
        DecompressionError: If there's an error during decompression
        DecodingError: If there's an error during decoding
        TokenizationError: If there's an error during detokenization
    """
    logger.info("Starting decompression")

    # Determine if input_data is a file path or binary data
    if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
        # It's a file path
        with operation_context(
            operation_name="File Reading",
            specific_exceptions={
                FileNotFoundError: (FileOperationError, "File not found: {error_message}"),
                PermissionError: (FileOperationError, "Permission denied: {error_message}")
            },
            fallback_exception=FileOperationError
        ):
            with open(input_data, "rb") as file:
                bin_data = file.read()
            logger.info(f"Read compressed data from file: {input_data} ({len(bin_data)} bytes)")
    else:
        # It's binary data
        if not isinstance(input_data, bytes):
            error_msg = f"Expected bytes object but got {type(input_data).__name__}"
            logger.error(error_msg)
            raise DecompressionError(error_msg)

        bin_data = input_data
        logger.info(f"Using provided binary data ({len(bin_data)} bytes)")

    # Step 1: Binary decoding
    with operation_context(
        operation_name="Binary Decoding",
        specific_exceptions={
            DecodingError: (DecodingError, "Error during binary decoding: {error_message}")
        },
        fallback_exception=DecompressionError
    ):
        tokens, encoded_window_size = decode_bytes(bin_data)
        logger.info(f"Decoded {len(tokens)} tokens with window size {encoded_window_size}")

    # Step 2: Split tokens into chunks at <BREAK> markers
    token_chunks = split_tokens_by_breaks(tokens)
    logger.info(f"Split into {len(token_chunks)} chunks at break markers")

    # Step 3: Detokenize all chunks and combine them
    with operation_context(
        operation_name="Detokenization",
        specific_exceptions={
            TokenizationError: (TokenizationError, "Error during detokenization: {error_message}")
        },
        fallback_exception=DecompressionError
    ):
        # Process each chunk individually since batch processing has been removed
        text = []
        for chunk in token_chunks:
            chunk_text = detokenize(chunk, model)
            text.append(chunk_text)
        logger.info(f"Detokenized all chunks")

    # Combine chunks if they came back as a list
    if isinstance(text, list):
        text = ''.join(text)
        logger.info(f"Combined detokenized chunks into {len(text)} bytes of text")

    # Save text if path provided
    if output_path:
        with operation_context(
            operation_name="File Saving",
            specific_exceptions={
                FileNotFoundError: (FileOperationError, "Output directory not found: {error_message}"),
                PermissionError: (FileOperationError, "Permission denied when saving output: {error_message}")
            },
            fallback_exception=FileOperationError
        ):
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(text)
            logger.info(f"Saved decompressed text to {output_path}")

    logger.info("Decompression complete")
    return text, tokens