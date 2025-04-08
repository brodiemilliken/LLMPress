import os
import sys
import argparse
import logging
from tabulate import tabulate


from Backend.utils.logging_config import configure_logging
from Backend.celery import CeleryClient
from Backend.Compression.compressor import compress
from Backend.Decompression.decompressor import decompress
from Backend.Test.test_utils.file_utils import compare_files
from Backend.config import get_preset  # Import the config module

def get_files_in_directory(directory_path):
    """
    Get all non-hidden files in a directory.
    """
    file_paths = []
    for file in os.listdir(directory_path):
        # Skip hidden files
        if not file.startswith('.'):
            full_path = os.path.join(directory_path, file)
            if os.path.isfile(full_path):
                file_paths.append(full_path)
    return file_paths

def process_file_in_memory(file_path, client, window_size, min_chunk=100, max_chunk=500, debug=False):
    """
    Process a single file with compression and decompression without writing to disk.
    """
    import time
    import tempfile

    # Get file name without directory
    file_name = os.path.basename(file_path)
    original_size = os.path.getsize(file_path)

    try:
        # First read the file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_text = f.read()
        except UnicodeDecodeError:
            # Try with alternative encoding if utf-8 fails
            with open(file_path, "r", encoding="latin-1") as f:
                original_text = f.read()

        # Print file being compressed (simple console output)
        print(f"Compressing: {file_name}")

        # Compress - no redundant logging
        start_time = time.time()
        bin_data, _, compressed_size, encoded_tokens = compress(
            file_path, client, window_size, None, min_chunk, max_chunk
        )
        compression_time = time.time() - start_time

        # Create temp directory for decompress output
        temp_dir = tempfile.mkdtemp()
        decompressed_temp_path = os.path.join(temp_dir, "decompressed.txt")

        # Print file being decompressed (simple console output)
        print(f"Decompressing: {file_name}")

        # Decompress - no redundant logging
        start_time = time.time()
        decoded_text, decoded_tokens = decompress(bin_data, client, decompressed_temp_path)
        decompression_time = time.time() - start_time

        # Read the decompressed content from the file
        with open(decompressed_temp_path, "r", encoding="utf-8", errors="replace") as f:
            decoded_text = f.read()

        # Check if content is identical using file-based comparison
        original_temp_path = os.path.join(temp_dir, "original.txt")
        with open(original_temp_path, "w", encoding="utf-8") as f:
            f.write(original_text)

        # Compare the files
        are_identical = compare_files(original_temp_path, decompressed_temp_path)

        # Calculate compression ratio
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

        # Clean up temp files
        try:
            os.remove(original_temp_path)
            os.remove(decompressed_temp_path)
            os.rmdir(temp_dir)
        except:
            pass

        return {
            "file_name": file_name,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": compression_ratio,
            "identical": are_identical,
            "compression_time": compression_time,
            "decompression_time": decompression_time
        }
    except Exception as e:
        logging.error(f"Error processing {file_name}: {str(e)}")

        return {
            "file_name": file_name,
            "original_size": original_size,
            "compressed_size": 0,
            "compression_ratio": 0,
            "identical": False,
            "compression_time": 0,
            "decompression_time": 0,
            "error": str(e)
        }

def process_directory(directory_path, client, window_size, min_chunk=100, max_chunk=500, debug=False):
    """
    Process all files in a directory.
    """
    file_paths = get_files_in_directory(directory_path)
    results = []

    print(f"Found {len(file_paths)} files to process in {directory_path}")

    for i, file_path in enumerate(file_paths, 1):
        print(f"\nFile {i}/{len(file_paths)}: {os.path.basename(file_path)}")
        result = process_file_in_memory(file_path, client, window_size, min_chunk, max_chunk, debug)
        results.append(result)

    return results

def display_results(results):
    """
    Display results in a table format using tabulate, with summary as the last row.
    """
    if not results:
        print("No files were processed.")
        return

    # Calculate overall statistics
    total_original = sum(r["original_size"] for r in results)
    total_compressed = sum(r["compressed_size"] for r in results)
    avg_ratio = total_original / total_compressed if total_compressed > 0 else 0
    total_savings = (1 - total_compressed/total_original) * 100 if total_original > 0 else 0
    total_identical = sum(1 for r in results if r["identical"])

    # Create detailed results table
    details_headers = ["File", "Original Size", "Compressed Size", "Ratio", "Savings", "Identical"]
    details_rows = []

    for r in results:
        savings = (1 - r["compressed_size"]/r["original_size"]) * 100 if r["original_size"] > 0 else 0
        details_rows.append([
            r["file_name"],
            f"{r['original_size']:,} bytes",
            f"{r['compressed_size']:,} bytes",
            f"{r['compression_ratio']:.2f}x",
            f"{savings:.2f}%",
            "Yes" if r["identical"] else "No"
        ])

    # Add the summary row
    details_rows.append([
        "SUMMARY",
        f"{total_original:,} bytes",
        f"{total_compressed:,} bytes",
        f"{avg_ratio:.2f}x",
        f"{total_savings:.2f}%",
        f"{total_identical}/{len(results)}"
    ])

    # Print the table with both individual files and summary
    print("\n=== Compression Results ===")
    print(tabulate(details_rows, headers=details_headers, tablefmt="grid"))

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLMPress compression on a folder of files")
    parser.add_argument("--input", "-i", required=True, help="Input directory with files to compress")
    parser.add_argument("--window-size", "-w", type=int, help="Size of the sliding context window (default: from config)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save files")
    parser.add_argument("--min-chunk", "-min", type=int, help="Minimum chunk size in bytes (default: from config)")
    parser.add_argument("--max-chunk", "-max", type=int, help="Maximum chunk size in bytes (default: from config)")
    parser.add_argument("--log-level", choices=["quiet", "normal", "verbose", "debug"],
                        default=None, help="Set logging verbosity (default: from config)")
    parser.add_argument("--model", "-m", default="gpt2", help="Model preset to use (default: gpt2)")

    args = parser.parse_args()

    # Load configuration based on model
    config = get_preset(args.model)

    # Get parameters from config if not specified
    window_size = args.window_size if args.window_size is not None else config.window_size()
    min_chunk = args.min_chunk if args.min_chunk is not None else config.min_chunk_size()
    max_chunk = args.max_chunk if args.max_chunk is not None else config.max_chunk_size()
    log_level = args.log_level if args.log_level is not None else config.log_level()

    # Configure logging
    configure_logging(log_level)

    # Validate input directory
    if not os.path.isdir(args.input):
        print(f"Error: Input directory '{args.input}' does not exist or is not a directory")
        return

    # Create client
    client = CeleryClient()

    # Print configuration
    print(f"\n=== Batch Processing Configuration ===")
    print(f"Input directory: {args.input}")
    print(f"Model preset: {args.model}")
    print(f"Window size: {window_size}")
    print(f"Min chunk size: {min_chunk} bytes")
    print(f"Max chunk size: {max_chunk} bytes")
    print(f"Debug mode: {'Enabled' if args.debug else 'Disabled'}")

    # Process directory
    print(f"=== Processing Directory: {args.input} ===")
    results = process_directory(args.input, client, window_size,
                               min_chunk, max_chunk, args.debug)

    # Display results
    display_results(results)


if __name__ == "__main__":
    main()