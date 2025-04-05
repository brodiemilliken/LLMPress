import sys
import os
from typing import Optional, Tuple, List, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Decompression import Detokenize
from Decompression import Decoder

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
    #print(tokens)    
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
        window_size (int): Size of the sliding context window for token prediction (default value if not encoded)
        output_path (str, optional): Path to save decompressed text
        
    Returns:
        tuple: (decompressed_text, decoded_tokens)
    """
    # Determine if input_data is a file path or binary data
    if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
        # It's a file path
        with open(input_data, "rb") as file:
            bin_data = file.read()
    else:
        # It's binary data
        bin_data = input_data
    
    # Step 1: Binary decoding - now also returns window size
    tokens, encoded_window_size = Decoder.decode_bytes(bin_data)
    # Use the encoded window size if available, otherwise use the provided default
    window_size = encoded_window_size if encoded_window_size > 0 else window_size
    
    # Step 2: Split tokens into chunks at <BREAK> markers
    token_chunks = split_tokens_by_breaks(tokens)
    
    # for token_chunk in token_chunks:
    #     print("Token chunk:")
    #     print(token_chunk)
    # Step 3: Detokenize all chunks and combine them
    text = Detokenize.detokenize_chunks(token_chunks, model, window_size)
    # Save text if path provided
    if output_path:
        if isinstance(text, list):
            text = ''.join(text)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)
    
    #print(text)
    
    return text, tokens

def decompress_to_chunks(input_data, model, window_size=64) -> Tuple[List[str], List[List[Any]]]:
    """
    Decompress binary data or a compressed file into separate chunks.
    
    Args:
        input_data (bytes or str): Binary data or path to compressed file
        model: The language model to use for detokenization
        window_size (int): Size of the sliding context window for token prediction (must match compression value)
        
    Returns:
        tuple: (list_of_text_chunks, list_of_token_chunks)
    """
    # Determine if input_data is a file path or binary data
    if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
        # It's a file path
        with open(input_data, "rb") as file:
            bin_data = file.read()
    else:
        # It's binary data
        bin_data = input_data
    
    # Step 1: Binary decoding
    tokens = Decoder.decode_bytes(bin_data)
    
    # Step 2: Split tokens into chunks at <BREAK> markers
    token_chunks = split_tokens_by_breaks(tokens)
    
    # Step 3: Detokenize each chunk separately
    text_chunks = []
    for chunk in token_chunks:
        chunk_text = Detokenize.decode_tokens(chunk, model, window_size)
        text_chunks.append(chunk_text)
    
    return text_chunks, token_chunks