"""
LLMPress Core Decompression Functionality

This module handles the decompression of binary data back to text.
"""
import os
import logging
from typing import Optional, Tuple, List, Any

# Import from within the decompression package
from .detokenizer import detokenize_chunks
from .decoder import decode_bytes
from ..exceptions import FileOperationError, DecompressionError, DecodingError, TokenizationError

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
    
    try:
        # Determine if input_data is a file path or binary data
        if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
            # It's a file path
            try:
                with open(input_data, "rb") as file:
                    bin_data = file.read()
                logger.info(f"Read compressed data from file: {input_data} ({len(bin_data)} bytes)")
            except Exception as e:
                logger.error(f"Error reading compressed file {input_data}: {str(e)}", exc_info=True)
                raise FileOperationError(f"Failed to read compressed file: {str(e)}")
        else:
            # It's binary data
            if not isinstance(input_data, bytes):
                error_msg = f"Expected bytes object but got {type(input_data).__name__}"
                logger.error(error_msg)
                raise DecompressionError(error_msg)
                
            bin_data = input_data
            logger.info(f"Using provided binary data ({len(bin_data)} bytes)")
        
        # Step 1: Binary decoding
        try:
            tokens, encoded_window_size = decode_bytes(bin_data)
            logger.info(f"Decoded {len(tokens)} tokens with window size {encoded_window_size}")
        except DecodingError as e:
            # Re-raise with more context
            raise DecodingError(f"Error during binary decoding: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during decoding: {str(e)}", exc_info=True)
            raise DecompressionError(f"Failed to decode binary data: {str(e)}")
        
        # Step 2: Split tokens into chunks at <BREAK> markers
        token_chunks = split_tokens_by_breaks(tokens)
        logger.info(f"Split into {len(token_chunks)} chunks at break markers")
        
        # Step 3: Detokenize all chunks and combine them
        try:
            text = detokenize_chunks(token_chunks, model, encoded_window_size)
            logger.info(f"Detokenized all chunks")
        except TokenizationError as e:
            # Re-raise with more context
            raise TokenizationError(f"Error during detokenization: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during detokenization: {str(e)}", exc_info=True)
            raise DecompressionError(f"Failed to detokenize chunks: {str(e)}")
        
        # Combine chunks if they came back as a list
        if isinstance(text, list):
            text = ''.join(text)
            logger.info(f"Combined detokenized chunks into {len(text)} bytes of text")
        
        # Save text if path provided
        if output_path:
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as file:
                    file.write(text)
                logger.info(f"Saved decompressed text to {output_path}")
            except Exception as e:
                logger.error(f"Error saving decompressed text to {output_path}: {str(e)}", exc_info=True)
                raise FileOperationError(f"Failed to save decompressed output: {str(e)}")
        
        logger.info("Decompression complete")
        return text, tokens
        
    except (FileOperationError, DecodingError, TokenizationError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during decompression: {str(e)}", exc_info=True)
        raise DecompressionError(f"Decompression failed: {str(e)}")