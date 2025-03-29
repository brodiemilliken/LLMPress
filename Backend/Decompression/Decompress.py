import sys
import os
from typing import Optional, Tuple, List, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Decompression import Detokenize
from Decompression import Decoder

def decompress(input_data, model, k=64, output_path=None) -> Tuple[str, List[Any]]:
    """
    Decompress binary data or a compressed file.
    
    Args:
        input_data (bytes or str): Binary data or path to compressed file
        model: The language model to use for detokenization
        k (int): Context window size (must match compression value)
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
    
    compressed_size = len(bin_data)
    
    # Step 1: Binary decoding
    tokens = Decoder.decode_bytes(bin_data)
    
    # Step 2: Detokenization
    text = Detokenize.decode_tokens(tokens, model, k)
    
    decompressed_size = len(text.encode('utf-8'))
    
    # Save text if path provided
    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)
    
    # Return just the text and tokens to match what process_file expects
    return text, tokens