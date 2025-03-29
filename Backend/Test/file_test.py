import os
import sys
import argparse
from tabulate import tabulate

# Fix the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Test_Utils import process_file, initialize_model

def display_results(result, output_dir="Output", debug=False):
    """
    Display results for a single file.
    
    Args:
        result (dict): Dictionary with metrics and results
        output_dir (str): Directory to save results file
        debug (bool): Whether debug mode is enabled
    """
    if not result:
        print("No file was processed.")
        return
    
    # Display results in a table format
    table_data = [
        ["File Name", result["file_name"]],
        ["Original Path", result["original_path"]],
        ["Compressed Path", result["compressed_path"]],
        ["Decompressed Path", result["decompressed_path"]],
        ["Original Size", f"{result['original_size']:,} bytes"],
        ["Compressed Size", f"{result['compressed_size']:,} bytes"],
        ["Compression Ratio", f"{result['compression_ratio']:.2f}x"],
        ["Space Savings", f"{(1 - result['compressed_size']/result['original_size']) * 100:.2f}%"],
        ["Compression Time", f"{result['compression_time']:.2f} seconds"],
        ["Decompression Time", f"{result['decompression_time']:.2f} seconds"],
        ["Files Identical", "Yes" if result["identical"] else "No"]
    ]
    
    # Add token comparison result if debug mode is on
    if debug and "tokens_identical" in result:
        table_data.append(["Tokens Identical", "Yes" if result["tokens_identical"] else "No"])
    
    print("\n=== Compression Results ===")
    print(tabulate(table_data, tablefmt="grid"))

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLMPress compression on a single file")
    parser.add_argument("--input", "-i", required=True, help="Path to the file to compress")
    parser.add_argument("--output", "-o", default="Output", help="Output directory for results")
    parser.add_argument("--k", type=int, default=64, help="Context window size (default: 64)")
    parser.add_argument("--model", default="gpt2", help="Model name to use (default: gpt2)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save token information")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Create model (default is now Celery)
    model = initialize_model(args.model)
    
    # Validate file path
    if not os.path.isfile(args.input):
        print(f"Error: File '{args.input}' does not exist or is not a file")
        return
        
    # Process file
    print(f"=== Processing File: {args.input} ===")
    result = process_file(args.input, model, args.k, args.output, verbose=True, debug=args.debug)
    
    # Display results
    display_results(result, args.output, debug=args.debug)


if __name__ == "__main__":
    main()