"""
Window Size Test

Tests the impact of window size on compression efficiency.
"""
import os
import sys
import argparse
import time
import logging
from tabulate import tabulate

# Import from Backend package
from Backend.celery_client import CeleryClient
from Backend.Compression.compressor import compress
from Backend.Decompression.decompressor import decompress
from Backend.config import get_preset
from Backend.utils.logging_config import configure_logging

def process_file_with_window_size(file_path, client, window_size, output_dir="Output", debug=False,
                               min_chunk=None, max_chunk=None):
    """
    Process a single file with a specific window size.
    
    Args:
        file_path: Path to the file to process
        client: The CeleryClient instance
        window_size: Size of the sliding context window
        output_dir: Directory to save output files
        debug: Whether to enable debug mode
        min_chunk: Minimum chunk size
        max_chunk: Maximum chunk size
        
    Returns:
        dict: Dictionary with metrics and results
    """
    # Get file name for display/output
    file_name = os.path.basename(file_path)
    
    # Create output directory structure
    window_dir = os.path.join(output_dir, f"window_{window_size}")
    os.makedirs(window_dir, exist_ok=True)
    
    # Set file paths
    compressed_path = os.path.join(window_dir, f"{file_name}.bin")
    decompressed_path = os.path.join(window_dir, f"decompressed_{file_name}")
    
    # Compress
    print(f"Compressing with window size {window_size}...")
    start_time = time.time()
    
    # Compress using file paths
    # Note: Fixed unpacking - compress returns 4 values
    bin_data, original_size, compressed_size, compression_tokens = compress(
        file_path, 
        client, 
        window_size,
        output_path=compressed_path,
        min=min_chunk,
        max=max_chunk
    )
    
    compression_time = time.time() - start_time
    
    # Decompress
    print(f"Decompressing with window size {window_size}...")
    start_time = time.time()
    
    # Decompress using file paths - fixed parameter order
    decoded_text, decompression_tokens = decompress(
        compressed_path, 
        client, 
        output_path=decompressed_path
    )
    
    decompression_time = time.time() - start_time
    
    # Read original file to check for identity
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        original_text = f.read()
    
    # Check if content is identical
    are_identical = (original_text == decoded_text)
    
    # Calculate compression ratio
    compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
    
    # Create result dictionary
    result = {
        "file_name": file_name,
        "original_path": file_path,
        "compressed_path": compressed_path,
        "decompressed_path": decompressed_path,
        "window_size": window_size,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "identical": are_identical,
        "compression_time": compression_time,
        "decompression_time": decompression_time
    }
    
    # Add token comparison if debug is enabled
    if debug:
        result["tokens_identical"] = (compression_tokens == decompression_tokens)
        
        # Save token information
        tokens_dir = os.path.join(window_dir, "tokens")
        os.makedirs(tokens_dir, exist_ok=True)
        
        # Save encoded tokens
        encoded_path = os.path.join(tokens_dir, f"{file_name}.encoded.txt")
        with open(encoded_path, "w", encoding="utf-8") as f:
            f.write("\n".join(map(str, compression_tokens)))
        
        # Save decoded tokens
        decoded_path = os.path.join(tokens_dir, f"{file_name}.decoded.txt")
        with open(decoded_path, "w", encoding="utf-8") as f:
            f.write("\n".join(map(str, decompression_tokens)))
    
    return result

def run_window_size_tests(file_path, client, start_size, num_tests, increment, 
                         output_dir="Output", debug=False, min_chunk=None, max_chunk=None):
    """
    Run compression tests with different window sizes on the same file.
    
    Args:
        file_path: Path to the test file
        client: The CeleryClient instance
        start_size: Starting window size
        num_tests: Number of tests to run
        increment: Window size increment between tests
        output_dir: Directory to save output files
        debug: Whether to save debug information
        min_chunk: Minimum chunk size
        max_chunk: Maximum chunk size
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    for i in range(num_tests):
        window_size = start_size + (i * increment)
        
        print(f"\n=== Test {i+1}/{num_tests}: Window Size = {window_size} ===")
        result = process_file_with_window_size(
            file_path, 
            client, 
            window_size, 
            output_dir, 
            debug,
            min_chunk,
            max_chunk
        )
        results.append(result)
        
    return results

def display_table_results(results):
    """
    Display test results in a table format.
    
    Args:
        results: List of test result dictionaries
    """
    table_data = []
    for r in results:
        row = [
            r["window_size"],
            f"{r['original_size']:,} bytes",
            f"{r['compressed_size']:,} bytes",
            f"{r['compression_ratio']:.2f}x",
            f"{(1 - r['compressed_size']/r['original_size']) * 100:.2f}%",
            f"{r['compression_time']:.2f}s",
            f"{r['decompression_time']:.2f}s",
            "Yes" if r["identical"] else "No"
        ]
        table_data.append(row)
    
    headers = ["Window Size", "Original Size", "Compressed Size", "Ratio", 
               "Space Savings", "Comp Time", "Decomp Time", "Files Match"]
    
    print("\n=== Window Size Benchmark Results ===")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLMPress compression with different window sizes")
    parser.add_argument("--input", "-i", required=True, help="Path to the file to compress")
    parser.add_argument("--output", "-o", default="Output", help="Output directory for results")
    parser.add_argument("--start-size", "-s", type=int, help="Starting window size (default: from config)")
    parser.add_argument("--num-tests", "-n", type=int, default=10, help="Number of tests to run (default: 10)")
    parser.add_argument("--increment", "-inc", type=int, default=16, help="Window size increment (default: 16)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save token information")
    parser.add_argument("--model", "-m", default="gpt2", help="Model preset to use for configuration")
    parser.add_argument("--min-chunk", "-min", type=int, help="Minimum chunk size in bytes (default: from config)")
    parser.add_argument("--max-chunk", "-max", type=int, help="Maximum chunk size in bytes (default: from config)")
    parser.add_argument("--log-level", choices=["quiet", "normal", "verbose", "debug"], 
                        default=None, help="Set logging verbosity (default: from config)")
    
    args = parser.parse_args()
    
    # Load configuration based on model
    config = get_preset(args.model)
    
    # Get parameters from config if not specified
    start_size = args.start_size if args.start_size is not None else config.window_size()
    min_chunk = args.min_chunk if args.min_chunk is not None else config.min_chunk_size()
    max_chunk = args.max_chunk if args.max_chunk is not None else config.max_chunk_size()
    log_level = args.log_level if args.log_level is not None else config.log_level()
    
    # Configure logging
    configure_logging(log_level)
    
    # Validate file path
    if not os.path.isfile(args.input):
        logging.error(f"Error: File '{args.input}' does not exist or is not a file")
        return
    
    # Get file name for display
    file_name = os.path.basename(args.input)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Create API client
    api = CeleryClient()
    
    # Print test configuration
    print("\n=== Window Size Benchmark Configuration ===")
    print(f"Input file: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"Model preset: {args.model}")
    print(f"Window size range: {start_size} to {start_size + (args.num_tests-1) * args.increment}")
    print(f"Number of tests: {args.num_tests}")
    print(f"Window size increment: {args.increment}")
    print(f"Chunk size range: {min_chunk} to {max_chunk} bytes")
    print(f"Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    
    # Run the benchmark
    start_time = time.time()
    results = run_window_size_tests(
        args.input, 
        api, 
        start_size, 
        args.num_tests, 
        args.increment, 
        args.output,
        args.debug,
        min_chunk,
        max_chunk
    )
    total_time = time.time() - start_time
    
    # Display results table
    display_table_results(results)
    
    # Print summary
    print(f"\nBenchmark completed in {total_time:.2f} seconds")
    
    # Find optimal window size based on compression ratio
    best_ratio_result = max(results, key=lambda r: r["compression_ratio"])
    best_ratio_window = best_ratio_result["window_size"]
    
    # Find optimal window size based on total processing time
    best_time_result = min(results, key=lambda r: r["compression_time"] + r["decompression_time"])
    best_time_window = best_time_result["window_size"]
    
    print("\n=== Recommendations ===")
    print(f"Best compression ratio: Window size = {best_ratio_window} ({best_ratio_result['compression_ratio']:.2f}x)")
    print(f"Fastest processing time: Window size = {best_time_window} ({best_time_result['compression_time'] + best_time_result['decompression_time']:.2f}s)")


if __name__ == "__main__":
    main()