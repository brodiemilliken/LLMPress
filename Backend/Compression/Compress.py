import sys
import os
from typing import Optional, Tuple, List, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Compression import Tokenize
from Compression import Encoder
from Compression import file_splitter

def combine_tokenized_chunks(tokenized_chunks: List[List[Tuple[str, int]]]) -> List[Tuple[str, int]]:
    """
    Combine multiple lists of tokenized chunks into a single flat list of tokens,
    with <BREAK> markers inserted between chunks.
    
    Args:
        tokenized_chunks: List of lists of token tuples
        
    Returns:
        List of token tuples with break markers between chunks
    """
    if not tokenized_chunks:
        return []
        
    # Special break token to mark chunk boundaries
    break_token = ("<BREAK>", 0)  # Using 0 as prediction value for special tokens
    
    combined_tokens = []
    
    # Add first chunk
    if tokenized_chunks[0]:
        combined_tokens.extend(tokenized_chunks[0])
    
    # Add remaining chunks with break tokens in between
    for chunk in tokenized_chunks[1:]:
        # Add break token before next chunk
        combined_tokens.append(break_token)
        
        # Add the chunk tokens
        if chunk:
            combined_tokens.extend(chunk)
    
    return combined_tokens

def compress(input_data, model, window_size=64, output_path=None, min=100, max=500) -> Tuple[bytes, int, int, List[Any]]:
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
    """
    # Determine original size
    if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
        original_size = os.path.getsize(input_data)
    else:
        original_size = len(input_data.encode('utf-8'))

    # Step 1: Chunk and tokenize
    chunks = file_splitter.chunk_file(input_data, min, max)
    tokenized_chunks = Tokenize.tokenize_chunks(chunks, model, window_size)
    
    # Combine all chunks into a single token list
    tokens = combine_tokenized_chunks(tokenized_chunks)
    
    # Step 2: Binary encoding
    bin_data = Encoder.encode_tokens(tokens.copy())
    compressed_size = len(bin_data)
    
    # Save binary if path provided
    if output_path:
        with open(output_path, "wb") as file:
            file.write(bin_data)
    
    return bin_data, original_size, compressed_size, tokens


