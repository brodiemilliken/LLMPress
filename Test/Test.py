import sys
import os
import time
import filecmp
import argparse
from tabulate import tabulate

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI.ChatGPT2 import GPT2
from Compression.Compress import compress
from Decompression.Decompress import decompress

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

def process_file(file_path, model, k, output_dir):
    """
    Process a single file with compression and decompression.
    
    Args:
        file_path (str): Path to the file to process
        model: The language model
        k (int): Context window size
        output_dir (str): Directory to store output files
        
    Returns:
        dict: Dictionary with metrics and results
    """
    # Create output directories if they don't exist
    compressed_dir = os.path.join(output_dir, "Compressed")
    results_dir = os.path.join(output_dir, "Results")
    os.makedirs(compressed_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    # Get file name without directory
    file_name = os.path.basename(file_path)
    
    # Define output paths
    compressed_path = os.path.join(compressed_dir, f"{file_name}.bin")
    decompressed_path = os.path.join(results_dir, f"{file_name}")
    
    # Start time
    start_time = time.time()
    
    # Compress
    bin_data, original_size, compressed_size = compress(
        file_path, 
        model, 
        k,
        compressed_path
    )
    
    compression_time = time.time() - start_time
    
    # Decompress
    start_time = time.time()
    decoded_text = decompress(compressed_path, model, k, decompressed_path)
    decompression_time = time.time() - start_time
    
    # Calculate compression ratio
    compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
    
    # Check if files are identical
    are_identical = compare_files(file_path, decompressed_path)
    
    return {
        "file_name": file_name,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "identical": are_identical,
        "compression_time": compression_time,
        "decompression_time": decompression_time
    }

def compare_files(original_path, reconstructed_path):
    """
    Compare two files to check if they're identical.
    
    Args:
        original_path (str): Path to the original file
        reconstructed_path (str): Path to the reconstructed file
        
    Returns:
        bool: True if files are identical, False otherwise
    """
    try:
        # First check if binary comparison shows they're identical
        if filecmp.cmp(original_path, reconstructed_path):
            return True
            
        # For text files, try a detailed content comparison
        with open(original_path, 'r', encoding='utf-8', errors='replace') as f1:
            original_content = f1.read()
        with open(reconstructed_path, 'r', encoding='utf-8', errors='replace') as f2:
            reconstructed_content = f2.read()
            
        return original_content == reconstructed_content
    except Exception as e:
        print(f"Error comparing files: {e}")
        return False

def process_directory(directory_path, model, k, output_dir="Output"):
    """
    Process all files in a directory.
    
    Args:
        directory_path (str): Path to the directory with files to process
        model: The language model
        k (int): Context window size
        output_dir (str): Directory to store output files
        
    Returns:
        list: List of dictionaries with metrics for each file
    """
    file_paths = get_files_in_directory(directory_path)
    results = []
    
    print(f"Found {len(file_paths)} files to process in {directory_path}")
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\nProcessing file {i}/{len(file_paths)}: {file_path}")
        result = process_file(file_path, model, k, output_dir)
        results.append(result)
        
    return results

def display_results(results, output_dir="Output"):
    """
    Display results in a nice table format.
    
    Args:
        results (list): List of result dictionaries
        output_dir (str): Directory to save results file
    """
    if not results:
        print("No files were processed.")
        return
        
    table_data = []
    for r in results:
        status = "✅ Identical" if r["identical"] else "❌ Different"
        table_data.append([
            r["file_name"],
            f"{r['original_size']:,} bytes",
            f"{r['compressed_size']:,} bytes",
            f"{r['compression_ratio']:.2f}x",
            f"{r['compression_time']:.2f}s",
            f"{r['decompression_time']:.2f}s",
            status
        ])
    
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
    
    # Save results to file
    results_file = os.path.join(output_dir, "compression_results.txt")
    with open(results_file, "w") as f:
        f.write("=== LLMPress Compression Results ===\n\n")
        f.write(tabulate(table_data, headers=headers, tablefmt="grid") + "\n\n")
        f.write(f"=== Overall Statistics ===\n")
        f.write(f"Total files processed: {len(results)}\n")
        f.write(f"Files with identical content: {total_identical}/{len(results)}\n")
        f.write(f"Total original size: {total_original:,} bytes\n")
        f.write(f"Total compressed size: {total_compressed:,} bytes\n")
        f.write(f"Average compression ratio: {avg_ratio:.2f}x\n")
        f.write(f"Space savings: {(1 - total_compressed/total_original) * 100:.2f}%\n")
    
    print(f"\nResults saved to: {results_file}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test LLMPress compression on a folder of files")
    parser.add_argument("--input", "-i", required=True, help="Input directory with files to compress")
    parser.add_argument("--output", "-o", default="Output", help="Output directory for results")
    parser.add_argument("--k", type=int, default=64, help="Context window size (default: 64)")
    parser.add_argument("--model", default="gpt2", help="Model name to use (default: gpt2)")
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.input):
        print(f"Error: Input directory '{args.input}' does not exist or is not a directory")
        return
        
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Create model
    print(f"Initializing model '{args.model}'...")
    model = GPT2(model_name=args.model)
    
    # Process directory
    print(f"=== Processing Directory: {args.input} ===")
    results = process_directory(args.input, model, args.k, args.output)
    
    # Display results
    display_results(results, args.output)


if __name__ == "__main__":
    main()