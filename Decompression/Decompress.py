import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Decompression import Decoder
from Decompression import Detokenize

def decompress(input_data, model, k=64, output_path=None):
    """
    Decompress binary data or a binary file.
    
    Args:
        input_data (bytes or str): Binary data or path to binary file
        model: The language model to use for tokenization
        k (int): Context window size
        output_path (str, optional): Path to save decoded text
        
    Returns:
        tuple: (decoded_text, decoded_tokens)
    """
    # Determine if input_data is a file path or binary data
    if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
        # It's a file path
        with open(input_data, "rb") as file:
            bin_data = file.read()
    else:
        # It's binary data
        bin_data = input_data
    
    # Decompression
    tokens = Decoder.decode_bytes(bin_data)
    text = Detokenize.decode_tokens(tokens.copy(), model, k)
    
    # Save text if path provided
    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)
    
    return text, tokens