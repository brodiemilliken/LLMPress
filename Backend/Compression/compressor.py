"""
LLMPress Core Compression Functionality

This module handles the compression of text data using language model predictions.
"""
import os
import logging
from typing import Tuple, List, Any

# Import from within the compression package
from .tokenizer import tokenize_chunks
from .encoder import encode_tokens
from .file_splitter import chunk_file
from ..exceptions import FileOperationError, CompressionError, TokenizationError, EncodingError
from ..utils.token_types import combine_token_chunks

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.Compressor')

def compress(input_data, model, window_size=100, output_path=None, min=100, max=500) -> Tuple[bytes, int, int, List[Any]]:
    """
    Compress a string or text file.

    Args:
        input_data (str): Text string or path to text file
        model: The language model to use for tokenization
        window_size (int): Size of the sliding context window for token prediction
        output_path (str, optional): Path to save binary output
        min: Minimum chunk size in bytes
        max: Maximum chunk size in bytes

    Returns:
        tuple: (binary_data, original_size, compressed_size, encoded_tokens)

    Raises:
        FileOperationError: If there's an error reading or writing files
        CompressionError: If there's an error during compression
        TokenizationError: If there's an error during tokenization
        EncodingError: If there's an error during encoding
    """
    logger.info(f"Starting compression with window size {window_size}")

    try:
        # Determine original size
        if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
            original_size = os.path.getsize(input_data)
            logger.info(f"Compressing file: {input_data} ({original_size} bytes)")
        else:
            # Assume input_data is a string if not a file path
            if not isinstance(input_data, str):
                raise CompressionError("Input data must be a string or a file path")
            original_size = len(input_data.encode('utf-8'))
            logger.info(f"Compressing string data ({original_size} bytes)")

        # Step 1: Chunk and tokenize
        try:
            chunks = chunk_file(input_data, min, max)
            logger.info(f"Created {len(chunks)} chunks")
        except FileOperationError as e:
            # Re-raise with more context
            raise FileOperationError(f"Error while chunking input: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during chunking: {str(e)}", exc_info=True)
            raise CompressionError(f"Failed to chunk input: {str(e)}")

        try:
            tokenized_chunks = tokenize_chunks(chunks, model, window_size)
            logger.info(f"Tokenized {len(tokenized_chunks)} chunks")
        except TokenizationError as e:
            # Re-raise with more context
            raise TokenizationError(f"Error during tokenization: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during tokenization: {str(e)}", exc_info=True)
            raise CompressionError(f"Failed to tokenize chunks: {str(e)}")

        # Combine all chunks into a single token list
        tokens = combine_token_chunks(tokenized_chunks)
        logger.info(f"Combined into {len(tokens)} tokens with break markers")

        # Step 2: Binary encoding
        try:
            bin_data = encode_tokens(tokens.copy(), window_size)
            compressed_size = len(bin_data)
            logger.info(f"Encoded to {compressed_size} bytes (ratio: {original_size/compressed_size:.2f}x)")
        except EncodingError as e:
            # Re-raise with more context
            raise EncodingError(f"Error during binary encoding: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during encoding: {str(e)}", exc_info=True)
            raise CompressionError(f"Failed to encode tokens: {str(e)}")

        # Save binary if path provided
        if output_path:
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "wb") as file:
                    file.write(bin_data)
                logger.info(f"Saved compressed data to {output_path}")
            except Exception as e:
                logger.error(f"Error saving compressed data to {output_path}: {str(e)}", exc_info=True)
                raise FileOperationError(f"Failed to save compressed output: {str(e)}")

        logger.info(f"Compression complete: {original_size} → {compressed_size} bytes")
        return bin_data, original_size, compressed_size, tokens

    except (FileOperationError, TokenizationError, EncodingError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during compression: {str(e)}", exc_info=True)
        raise CompressionError(f"Compression failed: {str(e)}")


