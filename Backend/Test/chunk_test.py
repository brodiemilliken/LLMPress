import os
import sys
import argparse
import hashlib

# Fix import path - add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # This points to Backend directory
sys.path.append(project_root)

# Now import should work - don't include "Backend." when running from within Backend directory
from Compression.file_splitter import chunk_file, split_text
from Compression.Tokenize import tokenize_chunks
from Decompression.Detokenize import detokenize
from celery_client import CeleryClient

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
    parser.add_argument("--min", "-m", type=int, default=50, help="Minimum chunk size in bytes")
    parser.add_argument("--max", "-M", type=int, default=300, help="Maximum chunk size in bytes")
    parser.add_argument("--window", "-w", type=int, default=64, help="Window size for tokenization")
    parser.add_argument("--tokenize", "-t", action="store_true", help="Also perform tokenization after chunking")
    parser.add_argument("--output", "-o", help="Output the reconstructed text to a file for comparison")
    
    args = parser.parse_args()
    
    # Test chunking
    chunks = test_file(args.input, args.min, args.max)
    
    # If requested, save the reconstructed text to verify manually
    if args.output and chunks:
        reconstructed = ''.join(chunks)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(reconstructed)
        print(f"\nReconstructed text saved to {args.output}")

    # Test tokenization if requested
    if args.tokenize and chunks:
        tokenized_chunks = test_tokenize(chunks, args.window)
        return chunks, tokenized_chunks
    
    return chunks


if __name__ == "__main__":
    main()