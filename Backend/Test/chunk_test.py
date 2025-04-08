import os
import sys
import argparse
import hashlib
import logging

# Import the simplified logging config
from Backend.utils.logging_config import configure_logging

# Import using proper package structure
from Backend.Compression.file_splitter import chunk_file, split_text
from Backend.Compression.tokenizer import tokenize_chunks
from Backend.Decompression.detokenizer import detokenize
from Backend.celery import CeleryClient
from Backend.config import get_preset  # Import the configuration system

def verify_data_integrity(original_text, chunks):
    """
    Verify that no data is lost during chunking.

    Args:
        original_text: Original text before chunking
        chunks: List of chunks after chunking

    Returns:
        tuple: (is_intact, original_hash, reconstructed_hash)
    """
    # Reconstruct text from chunks
    reconstructed_text = ''.join(chunks)

    # Compare lengths
    if len(original_text) != len(reconstructed_text):
        print(f"Length mismatch: Original {len(original_text)} vs Reconstructed {len(reconstructed_text)}")

        # Find where the difference starts
        for i, (orig_char, recon_char) in enumerate(zip(original_text, reconstructed_text)):
            if orig_char != recon_char:
                print(f"First difference at position {i}:")
                print(f"Original: '{original_text[i:i+20]}'")
                print(f"Reconstructed: '{reconstructed_text[i:i+20]}'")
                break

        # If reconstructed is shorter, show what's missing
        if len(original_text) > len(reconstructed_text):
            missing_start = len(reconstructed_text)
            print(f"Missing text from position {missing_start}:")
            print(f"'{original_text[missing_start:missing_start+50]}...'")

        # Calculate hashes anyway for diagnostic purposes
        original_hash = hashlib.md5(original_text.encode('utf-8')).hexdigest()
        reconstructed_hash = hashlib.md5(reconstructed_text.encode('utf-8')).hexdigest()
        return False, original_hash, reconstructed_hash

    # Calculate hashes for more robust comparison
    original_hash = hashlib.md5(original_text.encode('utf-8')).hexdigest()
    reconstructed_hash = hashlib.md5(reconstructed_text.encode('utf-8')).hexdigest()

    # Final validation
    if original_hash != reconstructed_hash:
        print("Hash mismatch despite same length - possible encoding issue!")
        return False, original_hash, reconstructed_hash

    return True, original_hash, reconstructed_hash

def test_file(file_path, min_chunk_size=50, max_chunk_size=300, verbose=True):
    """
    Test file chunking on a real file.

    Args:
        file_path: Path to the file to process
        min_chunk_size: Minimum chunk size in bytes
        max_chunk_size: Maximum chunk size in bytes
        verbose: Whether to display detailed output

    Returns:
        list: List of text chunks
    """
    try:
        # Validate file path
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist")
            return None

        # Get file type for display
        file_type = os.path.splitext(file_path)[1].lstrip('.')
        file_size = os.path.getsize(file_path)

        # Read the original file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                original_content = f.read()

        if verbose:
            print(f"\nProcessing file: {os.path.basename(file_path)}")
            print(f"File type: {file_type}")
            print(f"File size: {file_size} bytes")
            print(f"Min chunk size: {min_chunk_size} bytes")
            print(f"Max chunk size: {max_chunk_size} bytes")
            print("-" * 50)

        # Call the chunk_file function - now returns a list directly
        chunks = chunk_file(file_path, min_chunk_size, max_chunk_size)

        # Verify data integrity
        is_intact, original_hash, reconstructed_hash = verify_data_integrity(original_content, chunks)

        # Get sizes of each chunk
        chunk_sizes = [len(chunk) for chunk in chunks]

        if verbose:
            print(f"Created {len(chunks)} chunks:")
            for i, size in enumerate(chunk_sizes, 1):
                print(f"  Chunk {i}: {size} bytes")

            print(f"\nTotal original size: {file_size} bytes (on disk)")
            print(f"Original content size: {len(original_content)} bytes (in memory)")
            print(f"Total chunked size: {sum(chunk_sizes)} bytes")
            print(f"Average chunk size: {sum(chunk_sizes) / len(chunks):.1f} bytes")

            # Print data integrity verification results
            print("\n" + "="*20 + " DATA INTEGRITY " + "="*20)
            if is_intact:
                print("✅ INTEGRITY CHECK PASSED: No data loss during chunking")
            else:
                print("❌ INTEGRITY CHECK FAILED: Data lost during chunking")
                print(f"  Original hash: {original_hash}")
                print(f"  Reconstructed hash: {reconstructed_hash}")
                print(f"  Original length: {len(original_content)} bytes")
                print(f"  Reconstructed length: {len(''.join(chunks))} bytes")

        return chunks

    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_tokenize(chunks, window_size=64, verbose=True):
    """
    Test tokenization on a list of chunks.

    Args:
        chunks: List of text chunks to tokenize
        window_size: Size of the sliding context window for tokenization
        verbose: Whether to display detailed output

    Returns:
        list: List of tokenized chunks
    """
    try:
        if not chunks:
            print("No chunks to tokenize.")
            return None

        # Create client for tokenization
        client = CeleryClient()

        if verbose:
            print("\n" + "="*20 + " TOKENIZATION " + "="*20)
            print(f"Tokenizing {len(chunks)} chunks with window size {window_size}...")

        # Tokenize the chunks
        tokenized_chunks = tokenize_chunks(chunks, client, window_size)

        if verbose:
            # Print tokenization information
            token_counts = [len(chunk_tokens) for chunk_tokens in tokenized_chunks]
            total_tokens = sum(token_counts)

            print(f"Tokenized {len(tokenized_chunks)} chunks:")
            for chunk in tokenized_chunks:
                #print(chunk)  # Print first 10 tokens of each chunk")
                print(detokenize(chunk, client))  # Detokenize first 10 tokens for verification


            print(f"\nTotal tokens: {total_tokens}")
            print(f"Average tokens per chunk: {total_tokens / len(tokenized_chunks):.1f}")

        return tokenized_chunks

    except Exception as e:
        print(f"Error tokenizing chunks: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test text chunking and tokenization")
    parser.add_argument("--input", "-i", required=True, help="Path to the file to chunk")
    parser.add_argument("--min", "-m", type=int, help="Minimum chunk size in bytes (default: from config)")
    parser.add_argument("--max", "-M", type=int, help="Maximum chunk size in bytes (default: from config)")
    parser.add_argument("--window", "-w", type=int, help="Window size for tokenization (default: from config)")
    parser.add_argument("--tokenize", "-t", action="store_true", help="Also perform tokenization after chunking")
    parser.add_argument("--output", "-o", help="Output the reconstructed text to a file for comparison")
    parser.add_argument("--log-level", choices=["quiet", "normal", "verbose", "debug"],
                        default=None, help="Set logging verbosity (default: from config)")
    parser.add_argument("--model", default="gpt2", help="Model preset to use for configuration (default: gpt2)")

    args = parser.parse_args()

    # Load configuration based on model
    config = get_preset(args.model)

    # Get parameters from config if not specified
    window_size = args.window if args.window is not None else config.window_size()
    min_chunk = args.min if args.min is not None else config.min_chunk_size()
    max_chunk = args.max if args.max is not None else config.max_chunk_size()
    log_level = args.log_level if args.log_level is not None else config.log_level()

    # Configure logging with single parameter
    configure_logging(log_level)

    # Print configuration
    print(f"\n=== Chunk Test Configuration ===")
    print(f"Input file: {args.input}")
    print(f"Model preset: {args.model}")
    print(f"Min chunk size: {min_chunk} bytes")
    print(f"Max chunk size: {max_chunk} bytes")
    print(f"Window size: {window_size}")

    # Test chunking
    chunks = test_file(args.input, min_chunk, max_chunk)

    # If requested, save the reconstructed text to verify manually
    if args.output and chunks:
        reconstructed = ''.join(chunks)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(reconstructed)
        logging.info(f"Reconstructed text saved to {args.output}")

    # Test tokenization if requested
    if args.tokenize and chunks:
        tokenized_chunks = test_tokenize(chunks, window_size)
        return chunks, tokenized_chunks

    return chunks


if __name__ == "__main__":
    main()