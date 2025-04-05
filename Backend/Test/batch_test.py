import os
import sys
import argparse
from tabulate import tabulate

# Fix the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from celery_client import CeleryClient
from Compression.Compress import compress
from Decompression.Decompress import decompress
from Test_Utils.file_utils import compare_files

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
    
    Args:
        file_path: Path to the file to process
        client: The CeleryClient instance
        window_size: Size of the sliding context window
        min_chunk: Minimum chunk size in bytes
        max_chunk: Maximum chunk size in bytes
        debug: Whether to enable debug mode
        
    Returns:
        dict: Dictionary with metrics and results
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
        
        # Compress - pass the file path directly to compress function
        print(f"Compressing {file_name}...")
        start_time = time.time()
        bin_data, _, compressed_size, encoded_tokens = compress(
            file_path, client, window_size, None, min_chunk, max_chunk
        )
        compression_time = time.time() - start_time
        
        # Decompress
        print(f"Decompressing {file_name}...")
        start_time = time.time()
        decoded_text, decoded_tokens = decompress(bin_data, client, window_size)
        decompression_time = time.time() - start_time
        
        # Convert list to string if needed
        if isinstance(decoded_text, list):
            decoded_text = ''.join(decoded_text)
        
        # Check if content is identical using file-based comparison
        # This handles line ending differences and other subtle issues
        temp_dir = tempfile.mkdtemp()
        
        # Write original content to temp file
        original_temp_path = os.path.join(temp_dir, "original.txt")
        with open(original_temp_path, "w", encoding="utf-8") as f:
            f.write(original_text)
            
        # Write decoded content to temp file
        decoded_temp_path = os.path.join(temp_dir, "decoded.txt")
        with open(decoded_temp_path, "w", encoding="utf-8") as f:
            f.write(decoded_text)
            
        # Compare the files
        are_identical = compare_files(original_temp_path, decoded_temp_path)
        diff = "" if are_identical else "Files differ"

        # Print differences if not identical
        if not are_identical and debug:
            print("\nDifferences found between original and decompressed files:")
            print("Content differs - see debug output for details")
        
        # Calculate compression ratio
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        # Create output if debug is enabled
        if debug:
            # Create output directories
            output_dir = "Output/Debug"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save decompressed text
            decompressed_path = os.path.join(output_dir, f"decompressed_{file_name}")
            with open(decompressed_path, "w", encoding="utf-8") as f:
                f.write(decoded_text)
                
            # Save original text for comparison
            original_output_path = os.path.join(output_dir, f"original_{file_name}")
            with open(original_output_path, "w", encoding="utf-8") as f:
                f.write(original_text)
                
            # Save compressed data
            compressed_path = os.path.join(output_dir, f"{file_name}.bin")
            with open(compressed_path, "wb") as f:
                f.write(bin_data)
        
        # Clean up temp files
        try:
            os.remove(original_temp_path)
            os.remove(decoded_temp_path)
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
            "decompression_time": decompression_time,
            "diff": diff if not are_identical else ""
        }
    except Exception as e:
        print(f"Error processing {file_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        
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
        print(f"\nProcessing file {i}/{len(file_paths)}: {file_path}")
        result = process_file_in_memory(file_path, client, window_size, min_chunk, max_chunk, debug)
        results.append(result)
        
    return results

def display_results(results):
    """
    Display results in a nice table format.
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
        table_data.append(row)
    
    headers = ["File", "Original Size", "Compressed Size", "Ratio", "Comp Time", "Decomp Time", "Status"]
    
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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLMPress compression on a folder of files")
    parser.add_argument("--input", "-i", required=True, help="Input directory with files to compress")
    parser.add_argument("--window-size", "-w", type=int, default=64, 
                        help="Size of the sliding context window (default: 64)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode to save files")
    parser.add_argument("--min-chunk", "-min", type=int, default=100, help="Minimum chunk size in bytes (default: 100)")
    parser.add_argument("--max-chunk", "-max", type=int, default=500, help="Maximum chunk size in bytes (default: 500)")
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.input):
        print(f"Error: Input directory '{args.input}' does not exist or is not a directory")
        return
    
    # Create client
    client = CeleryClient()
    
    # Process directory
    print(f"=== Processing Directory: {args.input} ===")
    results = process_directory(args.input, client, args.window_size, 
                               args.min_chunk, args.max_chunk, args.debug)
    
    # Display results
    display_results(results)


if __name__ == "__main__":
    main()