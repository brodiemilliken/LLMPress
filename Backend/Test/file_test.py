import os
import sys
import argparse
import logging
import traceback
from tabulate import tabulate

from Backend.utils.logging_config import configure_logging
from Backend.utils.error_handler import log_exception
from Backend.exceptions import LLMPressError
from Backend.celery import CeleryClient
from Backend.config import get_preset
from test_utils import process_file

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
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Test LLMPress compression on a single file")
        parser.add_argument("--input", "-i", required=True, help="Path to the file to compress")
        parser.add_argument("--output", "-o", default="Output", help="Output directory for results")
        parser.add_argument("--window-size", "-w", type=int, help="Size of the sliding context window (default: from config)")
        parser.add_argument("--model", default="gpt2", help="Model preset to use (default: gpt2)")
        parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save token information")
        parser.add_argument("--min-chunk", "-min", type=int, help="Minimum chunk size in bytes (default: from config)")
        parser.add_argument("--max-chunk", "-max", type=int, help="Maximum chunk size in bytes (default: from config)")
        parser.add_argument("--log-level", choices=["quiet", "normal", "verbose", "debug"],
                            default=None, help="Set logging verbosity (default: from config)")

        args = parser.parse_args()

        # Load configuration based on model
        config = get_preset(args.model)

        # Get parameters from config if not specified
        window_size = args.window_size if args.window_size is not None else config.window_size()
        min_chunk = args.min_chunk if args.min_chunk is not None else config.min_chunk_size()
        max_chunk = args.max_chunk if args.max_chunk is not None else config.max_chunk_size()
        log_level = args.log_level if args.log_level is not None else config.log_level()

        # Configure logging with single parameter
        configure_logging(log_level)

        # Create output directory
        os.makedirs(args.output, exist_ok=True)

        # Create model (default is now Celery)
        api = CeleryClient()

        # Validate file path
        if not os.path.isfile(args.input):
            logging.error(f"Error: File '{args.input}' does not exist or is not a file")
            return

        # Process file
        logging.info(f"=== Processing File: {args.input} ===")
        print(f"Using model preset: {args.model}")
        print(f"Window size: {window_size}")
        print(f"Chunk size range: {min_chunk} to {max_chunk} bytes")

        result = process_file(args.input, api, window_size, args.output,
                            verbose=True, debug=args.debug,
                            min_chunk=min_chunk, max_chunk=max_chunk)

        # Display results
        display_results(result, args.output, debug=args.debug)

    except LLMPressError as e:
        # Handle known LLMPress errors
        logging.error(f"LLMPress error: {str(e)}")
        if hasattr(e, 'details') and e.details:
            logging.error(f"Details: {e.details}")
        if args.debug if 'args' in locals() else False:
            log_exception(e, "Error in file_test.py")
        sys.exit(1)
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {str(e)}")
        if 'args' in locals() and args.debug:
            traceback.print_exc()
        else:
            logging.error("Run with --debug for more information")
        sys.exit(1)


if __name__ == "__main__":
    main()