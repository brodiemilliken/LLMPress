#!/usr/bin/env python
"""
validator.py

Validates compressed files and compares decompression results with original files.
"""

import os
import argparse
import sys

def validate_compressed_file(file_path):
    """Validate a compressed file format before decompression."""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # Since compressed files are binary, just check if they exist and have content
    try:
        size = os.path.getsize(file_path)
        if size == 0:
            return False, "File is empty"
        return True, f"File exists with size: {size} bytes"
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def compare_with_original(original_file, decompressed_file):
    """Compare the original and decompressed files for debugging."""
    if not (os.path.exists(original_file) and os.path.exists(decompressed_file)):
        return "One or both files don't exist"
    
    with open(original_file, 'r', encoding='utf-8') as orig_f:
        original_text = orig_f.read()
    
    with open(decompressed_file, 'r', encoding='utf-8') as decomp_f:
        decompressed_text = decomp_f.read()
    
    # Compare the first 100 characters
    print("\nOriginal first 100 chars:")
    print(original_text[:100])
    print("\nDecompressed first 100 chars:")
    print(decompressed_text[:100])
    
    # Find the first difference
    min_len = min(len(original_text), len(decompressed_text))
    for i in range(min_len):
        if original_text[i] != decompressed_text[i]:
            print(f"\nFirst difference at position {i}:")
            start = max(0, i-10)
            end = min(min_len, i+10)
            print(f"Original: ...{original_text[start:end]}...")
            print(f"Decompressed: ...{decompressed_text[start:end]}...")
            return f"First difference at position {i}"
    
    if len(original_text) == len(decompressed_text):
        return "Files are identical"
    else:
        return f"Length mismatch: Original={len(original_text)}, Decompressed={len(decompressed_text)}"

def calculate_compression_ratio(compressed_file, original_file):
    """Calculate compression ratio between original and compressed files."""
    if not (os.path.exists(compressed_file) and os.path.exists(original_file)):
        return "One or both files don't exist"
    
    compressed_size = os.path.getsize(compressed_file)
    original_size = os.path.getsize(original_file)
    
    if original_size == 0:
        return "Unable to calculate ratio (original size is 0)"
    
    ratio = original_size / compressed_size
    savings = (1 - (compressed_size / original_size)) * 100
    
    return {
        'ratio': ratio,
        'compressed_size': compressed_size,
        'original_size': original_size,
        'savings_percent': savings,
        'summary': f"Compression ratio: {ratio:.2f}x ({original_size} bytes / {compressed_size} bytes = {savings:.2f}% saved)"
    }

def main():
    parser = argparse.ArgumentParser(description='Validate LLMPress compressed files and compare decompressed outputs')
    parser.add_argument('--compressed', '-c', required=True, help='Path to the compressed file')
    parser.add_argument('--decompressed', '-d', required=True, help='Path to the decompressed file')
    parser.add_argument('--original', '-o', help='Path to the original file for comparison')
    args = parser.parse_args()
    
    compressed_file = args.compressed
    decompressed_file = args.decompressed
    original_file = args.original
    
    # Validate the compressed file format
    print(f"Validating compressed file: {compressed_file}")
    valid, message = validate_compressed_file(compressed_file)
    if valid:
        print(f"✓ Compressed file validation: {message}")
    else:
        print(f"✗ Compressed file validation failed: {message}")
        return
    
    # Check if decompressed file exists
    if not os.path.exists(decompressed_file):
        print(f"✗ Decompressed file not found: {decompressed_file}")
        return
    else:
        print(f"✓ Decompressed file exists: {decompressed_file}")
    
    # If original file is provided, compare with decompressed and calculate compression ratio
    if original_file:
        if not os.path.exists(original_file):
            print(f"✗ Original file not found: {original_file}")
        else:
            print(f"\nComparing original with decompressed:")
            result = compare_with_original(original_file, decompressed_file)
            print(f"\nComparison result: {result}")
            
            # Calculate compression ratio
            compression_info = calculate_compression_ratio(compressed_file, original_file)
            if isinstance(compression_info, dict):
                print(f"\nCompression statistics:")
                print(f"- Original size: {compression_info['original_size']} bytes")
                print(f"- Compressed size: {compression_info['compressed_size']} bytes")
                print(f"- Compression ratio: {compression_info['ratio']:.2f}x")
                print(f"- Space saved: {compression_info['savings_percent']:.2f}%")
            else:
                print(f"\nCompression ratio: {compression_info}")

if __name__ == "__main__":
    main()
