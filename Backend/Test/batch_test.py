import os
import sys
import argparse
from tabulate import tabulate

# Fix the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Backend.celery_client import CeleryClient  # Correct import path
from Test_Utils import process_file

def get_files_in_directory(directory_path):
    """
    Get all non-hidden files in a directory.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        list: List of file paths
    """
    file_paths = []
    for file in os.listdir(directory_path):
        # Skip hidden files
        if not file.startswith('.'):
            full_path = os.path.join(directory_path, file)
            if os.path.isfile(full_path):
                file_paths.append(full_path)
    return file_paths

def process_directory(directory_path, model, window_size, output_dir="Output", debug=False):
    """
    Process all files in a directory.
    
    Args:
        directory_path (str): Path to the directory with files to process
        model: The language model
        window_size (int): Size of the sliding context window
        output_dir (str): Directory to store output files
        debug (bool): Whether to save debug information
        
    Returns:
        list: List of dictionaries with metrics for each file
    """
    file_paths = get_files_in_directory(directory_path)
    results = []
    
    print(f"Found {len(file_paths)} files to process in {directory_path}")
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\nProcessing file {i}/{len(file_paths)}: {file_path}")
        result = process_file(file_path, model, window_size, output_dir, verbose=True, debug=debug)
        results.append(result)
        
    return results

def display_results(results, output_dir="Output", debug=False):
    """
    Display results in a nice table format.
    
    Args:
        results (list): List of result dictionaries
        output_dir (str): Directory to save results file
        debug (bool): Whether debug mode is enabled
    """
    if not results:
        print("No files were processed.")
        return
        
    table_data = []
    for r in results:
        row = [
            r["file_name"],
            f"{r['original_size']:,} bytes",
            f"{r['compressed_size']:,} bytes",
            f"{r['compression_ratio']:.2f}x",
            f"{r['compression_time']:.2f}s",
            f"{r['decompression_time']:.2f}s",
            "Identical" if r["identical"] else "Different"
        ]
        
        # Add token comparison if debug mode is on
        if debug and "tokens_identical" in r:
            row.append("Yes" if r["tokens_identical"] else "No")
            
        table_data.append(row)
    
    headers = ["File", "Original Size", "Compressed Size", "Ratio", "Comp Time", "Decomp Time", "Status"]
    
    # Add token comparison header if debug mode is on
    if debug and results and "tokens_identical" in results[0]:
        headers.append("Tokens Match")
    
    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Calculate and display overall statistics
    total_original = sum(r["original_size"] for r in results)
    total_compressed = sum(r["compressed_size"] for r in results)
    avg_ratio = total_original / total_compressed if total_compressed > 0 else 0
    total_identical = sum(1 for r in results if r["identical"])
    
    print(f"\n=== Overall Statistics ===")
    print(f"Total files processed: {len(results)}")
    print(f"Files with identical content: {total_identical}/{len(results)}")
    print(f"Total original size: {total_original:,} bytes")
    print(f"Total compressed size: {total_compressed:,} bytes")
    print(f"Average compression ratio: {avg_ratio:.2f}x")
    print(f"Space savings: {(1 - total_compressed/total_original) * 100:.2f}%")
    
    # Display token match stats if debug mode is on
    if debug and results and "tokens_identical" in results[0]:
        total_tokens_identical = sum(1 for r in results if r.get("tokens_identical", False))
        print(f"Files with identical tokens: {total_tokens_identical}/{len(results)}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLMPress compression on a folder of files")
    parser.add_argument("--input", "-i", required=True, help="Input directory with files to compress")
    parser.add_argument("--output", "-o", default="Output", help="Output directory for results")
    parser.add_argument("--window-size", "-w", type=int, default=64, 
                        help="Size of the sliding context window (default: 64)")
    parser.add_argument("--model", default="gpt2", help="Model name to use (default: gpt2)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save token information")
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.input):
        print(f"Error: Input directory '{args.input}' does not exist or is not a directory")
        return
        
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Create model (default is now Celery)
    api = CeleryClient()
    
    # Process directory
    print(f"=== Processing Directory: {args.input} ===")
    results = process_directory(args.input, api, args.window_size, args.output, debug=args.debug)
    
    # Display results
    display_results(results, args.output, debug=args.debug)


if __name__ == "__main__":
    main()