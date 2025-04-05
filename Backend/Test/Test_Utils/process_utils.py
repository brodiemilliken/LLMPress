import os
import time

# Import using proper package structure
from Backend.Compression.compressor import compress
from Backend.Decompression.decompressor import decompress
from .file_utils import create_output_dirs, compare_files
from .token_utils import compare_tokens, save_debug_info, save_token_comparison

def process_file(file_path, model, window_size, output_dir, verbose=False, debug=False, min_chunk=100, max_chunk=500):
    """
    Process a single file with compression and decompression.
    
    Args:
        file_path (str): Path to the file to process
        model: The language model
        window_size (int): Size of the sliding context window for token prediction
        output_dir (str): Directory to store output files
        verbose (bool): Whether to print detailed information
        debug (bool): Whether to save debug information
        min_chunk (int): Minimum chunk size in bytes
        max_chunk (int): Maximum chunk size in bytes
        
    Returns:
        dict: Dictionary with metrics and results
    """
    # Create output directories
    compressed_dir, results_dir, debug_dir = create_output_dirs(output_dir, debug)
    
    # Get file name without directory
    file_name = os.path.basename(file_path)
    
    # Define output paths
    compressed_path = os.path.join(compressed_dir, f"{file_name}.bin")
    decompressed_path = os.path.join(results_dir, f"{file_name}")
    
    if verbose:
        print(f"Original file: {file_path}")
        print(f"Compressed file will be saved to: {compressed_path}")
        print(f"Decompressed file will be saved to: {decompressed_path}")
        if debug:
            print(f"Debug information will be saved to: {debug_dir}")
    
    # Start time
    start_time = time.time()
    
    # Compress
    if verbose:
        print("\nCompressing file...")
    bin_data, original_size, compressed_size, encoded_tokens = compress(
        file_path, 
        model, 
        window_size,
        compressed_path,
        min_chunk,
        max_chunk
    )
    
    compression_time = time.time() - start_time
    
    # Decompress
    if verbose:
        print("\nDecompressing file...")
    start_time = time.time()
    decoded_text, decoded_tokens = decompress(compressed_path, model, decompressed_path)
    decompression_time = time.time() - start_time
    
    # Compare tokens
    tokens_match = False
    if debug:
        tokens_match, differences = compare_tokens(encoded_tokens, decoded_tokens)
    
    # Save debug information if requested
    if debug and debug_dir:
        encoded_debug_path = os.path.join(debug_dir, f"{file_name}.encoded_tokens.txt")
        decoded_debug_path = os.path.join(debug_dir, f"{file_name}.decoded_tokens.txt")
        comparison_path = os.path.join(debug_dir, f"{file_name}.token_comparison.txt")
        
        if verbose:
            print(f"Saving encoded tokens to: {encoded_debug_path}")
            print(f"Saving decoded tokens to: {decoded_debug_path}")
            print(f"Saving token comparison to: {comparison_path}")
            
        save_debug_info(encoded_tokens, encoded_debug_path, "encoded")
        save_debug_info(decoded_tokens, decoded_debug_path, "decoded")
        #save_token_comparison(encoded_tokens, decoded_tokens, comparison_path)
    
    # Calculate compression ratio
    compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
    
    # Check if files are identical
    if verbose:
        print("\nComparing original and decompressed files...")
    are_identical = compare_files(file_path, decompressed_path)
    
    return {
        "file_name": file_name,
        "original_path": file_path,
        "compressed_path": compressed_path,
        "decompressed_path": decompressed_path,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "identical": are_identical,
        "tokens_identical": tokens_match,
        "compression_time": compression_time,
        "decompression_time": decompression_time
    }

def process_string(text_string, model, window_size, output_dir, verbose=False, debug=False):
    """
    Process a text string with compression and decompression.
    
    Args:
        text_string (str): The string to process
        model: The language model
        window_size (int): Size of the sliding context window for token prediction
        output_dir (str): Directory to store output files
        verbose (bool): Whether to print detailed information
        debug (bool): Whether to save debug information
        
    Returns:
        dict: Dictionary with metrics and results
    """
    # Create output directories
    compressed_dir, results_dir, debug_dir = create_output_dirs(output_dir, debug)
    
    # Define output paths
    string_file = os.path.join(output_dir, "input_string.txt")
    compressed_path = os.path.join(compressed_dir, "input_string.bin")
    decompressed_path = os.path.join(results_dir, "input_string.txt")
    
    # Save the input string to a file for comparison
    with open(string_file, "w", encoding="utf-8") as f:
        f.write(text_string)
    
    if verbose:
        print(f"Input string saved to: {string_file}")
        print(f"Compressed file will be saved to: {compressed_path}")
        print(f"Decompressed file will be saved to: {decompressed_path}")
        if debug:
            print(f"Debug information will be saved to: {debug_dir}")
    
    # Start time
    start_time = time.time()
    
    # Compress
    if verbose:
        print("\nCompressing string...")
    bin_data, original_size, compressed_size, encoded_tokens = compress(
        text_string, 
        model, 
        window_size,
        compressed_path
    )
    
    compression_time = time.time() - start_time
    
    # Decompress
    if verbose:
        print("\nDecompressing data...")
    start_time = time.time()
    decoded_text, decoded_tokens = decompress(compressed_path, model, window_size, decompressed_path)
    decompression_time = time.time() - start_time
    
    # Compare tokens
    tokens_match = False
    if debug:
        tokens_match, differences = compare_tokens(encoded_tokens, decoded_tokens)
    
    # Save debug information if requested
    if debug and debug_dir:
        encoded_debug_path = os.path.join(debug_dir, "input_string.encoded_tokens.txt")
        decoded_debug_path = os.path.join(debug_dir, "input_string.decoded_tokens.txt")
        comparison_path = os.path.join(debug_dir, "input_string.token_comparison.txt")
        
        if verbose:
            print(f"Saving encoded tokens to: {encoded_debug_path}")
            print(f"Saving decoded tokens to: {decoded_debug_path}")
            print(f"Saving token comparison to: {comparison_path}")
            
        save_debug_info(encoded_tokens, encoded_debug_path, "encoded")
        save_debug_info(decoded_tokens, decoded_debug_path, "decoded")
        #save_token_comparison(encoded_tokens, decoded_tokens, comparison_path)
    
    # Calculate compression ratio
    compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
    
    # Check if strings are identical
    are_identical = (text_string == decoded_text)
    
    return {
        "file_name": "input_string.txt",
        "original_path": string_file,
        "compressed_path": compressed_path,
        "decompressed_path": decompressed_path,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "identical": are_identical,
        "tokens_identical": tokens_match,
        "compression_time": compression_time,
        "decompression_time": decompression_time
    }