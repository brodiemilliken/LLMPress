"""
LLMPress Core Decompression Functionality

This module handles the decompression of binary data back to text.
"""
import os
from typing import Optional, Tuple, List, Any

# Import from within the decompression package
from .detokenizer import detokenize_chunks
from .decoder import decode_bytes

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
    tokens, encoded_window_size = decode_bytes(bin_data)
    
    # Step 2: Split tokens into chunks at <BREAK> markers
    token_chunks = split_tokens_by_breaks(tokens)
    
    # Step 3: Detokenize all chunks and combine them
    text = detokenize_chunks(token_chunks, model, encoded_window_size)
    
    # Combine chunks if they came back as a list
    if isinstance(text, list):
        text = ''.join(text)
    
    # Save text if path provided
    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)
    
    return text, tokens