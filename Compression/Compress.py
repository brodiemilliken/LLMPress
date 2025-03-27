import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Compression import Tokenize
from Compression import Encoder

def compress(input_data, model, k=64, output_path=None):
    """
    Compress a string or text file.
    
    Args:
        input_data (str): Text string or path to text file
        model: The language model to use for tokenization
        k (int): Context window size
        output_path (str, optional): Path to save binary output
        
    Returns:
        tuple: (binary_data, original_size, compressed_size)
    """
    # Determine if input_data is a file path or a string
    if isinstance(input_data, str) and os.path.exists(input_data) and os.path.isfile(input_data):
        # It's a file path
        with open(input_data, "r", encoding="utf-8") as file:
            text = file.read()
        original_size = os.path.getsize(input_data)
    else:
        # It's a string
        text = input_data
        original_size = len(text.encode('utf-8'))
    
    # Compression
    tokens = Tokenize.encode_text(text, model, k)
    bin_data = Encoder.encode_tokens(tokens)
    compressed_size = len(bin_data)
    
    # Save binary if path provided
    if output_path:
        with open(output_path, "wb") as file:
            file.write(bin_data)
    
    return bin_data, original_size, compressed_size