#!/usr/bin/env python
"""
decompress.py

This script reads a binary file produced by compress.py and reconstructs the original text.
It decodes our custom binary format:
  - A byte with MSB 0 encodes a rank token; its payload (6 bits) is the rank (0–63).
  - A byte with MSB 1 starts a raw token. Raw tokens are encoded in variable-length base‑64:
      * Each byte has bit7=1.
      * Bytes with bit6=0 indicate more data.
      * The first byte encountered with bit6=1 marks the end of the raw token.
  - For raw tokens, if the decoded integer is less than 64, we assume it encodes an ASCII character
    (and add 32 to recover the original ASCII code) to obtain the corresponding token ID via the tokenizer.
  - Otherwise, the decoded integer is treated as the explicit token ID.
  
For rank tokens, the model is used (with the given context) to select the token based on its rank from the top 64 predictions.
"""

import os
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import argparse
import gzip
from tqdm import tqdm

def decode_varint(byte_stream, start_index):
    """
    Decode a variable-length integer (raw token) from byte_stream starting at start_index.
    Each byte has:
      - Bit 7: always 1.
      - Bit 6: termination flag (1 = last byte in the token encoding).
      - Bits 5–0: payload.
    Returns a tuple: (decoded integer, next_index).
    """
    value = 0
    shift = 0
    i = start_index
    while i < len(byte_stream):
        byte = byte_stream[i]
        payload = byte & 0x3F
        value |= (payload << shift)
        if (byte & 0x40) != 0:  # termination flag is set
            i += 1
            break
        i += 1
        shift += 6
    return value, i

def safe_token_id(token_id, vocab_size, verbose=False):
    """Ensure token ID is within the valid range for the vocabulary"""
    if token_id < 0:
        if verbose:
            print(f"Warning: Negative token ID {token_id}, using 0 instead")
        return 0
    if token_id >= vocab_size:
        if verbose:
            print(f"Warning: Token ID {token_id} out of range (max: {vocab_size-1}), using UNK token instead")
        return 0
    return token_id

def decode_byte_stream(byte_stream, tokenizer, top_k=64, verbose=False):
    """
    Decode the custom binary format into a list of token IDs.
    For rank tokens (MSB 0), use model predictions (with context) to select the token by rank.
    For raw tokens (MSB 1), decode the variable-length integer:
      - If the decoded integer is less than 64, assume it encodes an ASCII character (value + 32).
      - Otherwise, treat it as an explicit token ID.
    """
    # Stats to track different token types
    stats = {"rank_tokens": 0, "ascii_tokens": 0, "explicit_tokens": 0}
    
    tokens = []
    i = 0
    n = len(byte_stream)
    
    vocab_size = tokenizer.vocab_size
    if verbose:
        print(f"Tokenizer vocabulary size: {vocab_size}")
    
    # Load the model for rank token prediction.
    print("Loading GPT-2 model for token prediction...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    model.to(device)
    model.eval()
    print(f"Using device: {device}")
    
    # Estimate the number of tokens (for progress bar)
    # This is a rough estimate - each token is at least 1 byte
    estimated_tokens = n
    
    print("Decoding binary data...")
    # Use tqdm for a progress bar during decoding
    with tqdm(total=estimated_tokens, desc="Decoding", unit="byte", disable=verbose) as pbar:
        while i < n:
            pbar.update(1)  # Update progress by 1 byte by default
            
            byte = byte_stream[i]
            if ((byte >> 7) & 1) == 0:
                # Rank token: bits = [0][0][6-bit rank]
                rank = byte & 0x3F
                stats["rank_tokens"] += 1
                
                if not tokens:
                    token_id = rank
                else:
                    try:
                        context_tensor = torch.tensor([tokens], dtype=torch.long, device=device)
                        with torch.no_grad():
                            outputs = model(context_tensor)
                            logits = outputs.logits[0, -1, :]
                        topk_indices = torch.topk(logits, k=min(top_k, vocab_size), dim=-1).indices.squeeze().tolist()
                        if rank < len(topk_indices):
                            token_id = topk_indices[rank]
                        else:
                            token_id = topk_indices[0]
                    except Exception as e:
                        if verbose:
                            print(f"Error during rank token prediction: {e}")
                        token_id = rank
                
                token_id = safe_token_id(token_id, vocab_size, verbose)
                tokens.append(token_id)
                i += 1
            else:
                # Raw token: decode variable-length integer
                try:
                    start_i = i  # Save starting position to update progress bar correctly
                    raw_value, i = decode_varint(byte_stream, i)
                    pbar.update(i - start_i - 1)  # Adjust progress for multi-byte tokens
                    
                    if raw_value < 64:
                        # ASCII token
                        ascii_code = raw_value + 32
                        token_ids = tokenizer.encode(chr(ascii_code), add_special_tokens=False)
                        token_id = token_ids[0] if token_ids else raw_value
                        stats["ascii_tokens"] += 1
                    else:
                        # Explicit token ID
                        token_id = raw_value
                        stats["explicit_tokens"] += 1
                    
                    token_id = safe_token_id(token_id, vocab_size, verbose)
                    tokens.append(token_id)
                except Exception as e:
                    if verbose:
                        print(f"Error during raw token decoding at position {i}: {e}")
                    i += 1  # Skip this byte to avoid infinite loop
    
    # Print stats for the decoding process
    total = sum(stats.values())
    if total > 0:  # Avoid division by zero
        print("\nDecoding statistics:")
        print(f"- Rank tokens: {stats['rank_tokens']} ({stats['rank_tokens']/total*100:.2f}%)")
        print(f"- ASCII tokens: {stats['ascii_tokens']} ({stats['ascii_tokens']/total*100:.2f}%)")
        print(f"- Explicit tokens: {stats['explicit_tokens']} ({stats['explicit_tokens']/total*100:.2f}%)")
    
    return tokens

def decompress_text(compressed_file, output_file=None, top_k=64, verbose=False):
    print(f"Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    
    # If the file ends with .gz, use gzip to decompress; otherwise, read normally.
    if compressed_file.endswith('.gz'):
        f_open = lambda path, mode: gzip.open(path, mode)
    else:
        f_open = open
    try:
        with f_open(compressed_file, 'rb') as f:
            byte_stream = f.read()
        print(f"Loaded compressed file: {len(byte_stream)} bytes")
        
        token_ids = decode_byte_stream(byte_stream, tokenizer, top_k=top_k, verbose=verbose)
        print(f"Decoded {len(token_ids)} tokens")
        
        if not token_ids:
            print("Warning: No tokens were decoded from the file")
            decoded_text = ""
        else:
            print("Converting tokens to text...")
            vocab_size = tokenizer.vocab_size
            token_ids = [safe_token_id(tid, vocab_size, verbose) for tid in token_ids]
            decoded_text = tokenizer.decode(token_ids)
        
        if output_file:
            print(f"Writing output to {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(decoded_text)
            print(f"Decompressed text saved to {output_file}")
        return decoded_text
    except Exception as e:
        print(f"Error during decompression: {e}")
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("")
            print(f"Created empty output file due to error: {output_file}")
        return ""

def main():
    parser = argparse.ArgumentParser(
        description="Decompress a binary file produced by LLMPress custom encoder."
    )
    parser.add_argument("input_file", help="Path to the compressed binary file")
    parser.add_argument("--output", "-o", help="Path for the decompressed output text file")
    parser.add_argument("--top-k", type=int, default=64, help="Top predictions to consider (default 64)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed token information")
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output if args.output else "decompressed.txt"
    
    print(f"Reading compressed data from: {input_file}")
    decoded_text = decompress_text(input_file, output_file, top_k=args.top_k, verbose=args.verbose)
    print("\nDecompression complete.")
    print(f"Decompressed text length: {len(decoded_text)} characters")
    print("First 100 characters:")
    print(decoded_text[:100])
    
if __name__ == "__main__":
    main()
