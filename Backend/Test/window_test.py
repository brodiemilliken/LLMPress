import os
import sys
import argparse
import time
from tabulate import tabulate

# Fix the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Backend.celery_client import CeleryClient
from Compression.Compress import compress
from Decompression.Decompress import decompress

def process_file_in_memory(file_path, client, window_size, debug=False):
    """
    Process a single file with compression and decompression without writing to disk.
    
    Args:
        file_path: Path to the file to process
        client: The CeleryClient instance
        window_size: Size of the sliding context window
        debug: Whether to enable debug mode
        
    Returns:
        dict: Dictionary with metrics and results
    """
    # Get file name without directory
    file_name = os.path.basename(file_path)
    
    # Read the input file
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    original_size = os.path.getsize(file_path)
    
    # Compress
    print(f"Compressing with window size {window_size}...")
    start_time = time.time()
    bin_data, _, compressed_size, encoded_tokens = compress(text, client, window_size)
    compression_time = time.time() - start_time
    
    # Decompress
    print(f"Decompressing with window size {window_size}...")
    start_time = time.time()
    decoded_text, decoded_tokens = decompress(bin_data, client, window_size)
    decompression_time = time.time() - start_time
    
    # Check if content is identical
    are_identical = (text == decoded_text)
    
    # Calculate compression ratio
    compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
    
    # Create result dictionary
    result = {
        "file_name": file_name,
        "window_size": window_size,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "identical": are_identical,
        "compression_time": compression_time,
        "decompression_time": decompression_time
    }
    
    # Create output if debug is enabled
    if debug:
        # Create output directories
        output_dir = f"Output/Debug/window_{window_size}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save decompressed text
        decompressed_path = os.path.join(output_dir, f"decompressed_{file_name}")
        with open(decompressed_path, "w", encoding="utf-8") as f:
            f.write(decoded_text)
            
        # Save compressed data
        compressed_path = os.path.join(output_dir, f"{file_name}.bin")
        with open(compressed_path, "wb") as f:
            f.write(bin_data)
            
        print(f"Debug files saved to {output_dir}")
    
    return result

def run_window_size_tests(file_path, client, start_size, num_tests, increment, debug=False):
    """
    Run compression tests with different window sizes on the same file.
    
    Args:
        file_path: Path to the test file
        client: The CeleryClient instance
        start_size: Starting window size
        num_tests: Number of tests to run
        increment: Window size increment between tests
        debug: Whether to save debug information
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    for i in range(num_tests):
        window_size = start_size + (i * increment)
        
        print(f"\n=== Test {i+1}/{num_tests}: Window Size = {window_size} ===")
        result = process_file_in_memory(file_path, client, window_size, debug)
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
    parser.add_argument("--start-size", "-s", type=int, default=20, help="Starting window size (default: 20)")
    parser.add_argument("--num-tests", "-n", type=int, default=10, help="Number of tests to run (default: 10)")
    parser.add_argument("--increment", "-inc", type=int, default=16, help="Window size increment (default: 16)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save files")
    
    args = parser.parse_args()
    
    # Validate file path
    if not os.path.isfile(args.input):
        print(f"Error: File '{args.input}' does not exist or is not a file")
        return
    
    # Get file name for display
    file_name = os.path.basename(args.input)
    
    # Create API client
    api = CeleryClient()
    
    # Print test configuration
    print("\n=== Window Size Benchmark Configuration ===")
    print(f"Input file: {args.input}")
    print(f"Window size range: {args.start_size} to {args.start_size + (args.num_tests-1) * args.increment}")
    print(f"Number of tests: {args.num_tests}")
    print(f"Window size increment: {args.increment}")
    print(f"Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    
    # Run the benchmark
    start_time = time.time()
    results = run_window_size_tests(
        args.input, 
        api, 
        args.start_size, 
        args.num_tests, 
        args.increment, 
        args.debug
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