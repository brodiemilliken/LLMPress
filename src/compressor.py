#!/usr/bin/env python
"""
compress.py

This script compresses a text file using an LLM predictability approach and
encodes each token into a custom binary format. The format is as follows:

For a **rank token** (if the token is among the top 64 predictions):
  - 1 byte:
    - Bit 7 = 0 (indicates rank encoding)
    - Bit 6 = 0 (unused)
    - Bits 5–0: rank (0–63)

For an **explicit raw token** (if not in top predictions or for the first token):
  - Variable-length encoding using base‑64 digits:
    - Each byte has Bit 7 = 1.
    - All bytes except the last have Bit 6 = 0.
    - The final byte has Bit 6 = 1 to signal termination.
    - Bits 5–0 hold chunks (6 bits each) of the token’s value.
  - Additionally, if the token represents a common ASCII character (and its ASCII code is between 32 and 95),
    we encode the value as (ascii_code – 32) so that it fits in one byte.
"""

import os
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import argparse
from tqdm import tqdm

def encode_rank_token(rank):
    """Encode a rank token (raw flag = 0) into one byte.
       Rank must be in 0–63.
       Layout: [0][0][6-bit rank]"""
    return bytes([rank & 0x3F])

def encode_raw_token(value):
    """
    Encode a raw token (raw flag = 1) into one or more bytes using variable-length base-64 encoding.
    Each byte: bit7=1.
      - For intermediate bytes, bit6=0.
      - For the final byte, bit6=1 (acts as the terminator).
    The 6-bit payloads (bits 5–0) are in little-endian order.
    """
    result = []
    while value >= 64:
        # Intermediate byte: raw flag=1, termination=0, payload = lower 6 bits.
        result.append((1 << 7) | (0 << 6) | (value & 0x3F))
        value >>= 6
    # Final byte: raw flag=1, termination flag=1, payload = remaining value.
    result.append((1 << 7) | (1 << 6) | (value & 0x3F))
    return bytes(result)

def safe_token_id(token_id, vocab_size):
    """Ensure token ID is within valid vocabulary range"""
    if token_id >= vocab_size:
        print(f"Warning: Token ID {token_id} exceeds vocabulary size {vocab_size}. Using UNK token.")
        return 0  # Use UNK token (usually token 0)
    return token_id

def build_ascii_mapping(tokenizer, verbose=False):
    """Build comprehensive mapping between token IDs and ASCII characters"""
    ascii_token_map = {}
    token_to_ascii = {}
    
    # Map each printable ASCII character to its token ID(s)
    if verbose:
        print("Building ASCII character mapping...")
    for ascii_code in range(32, 127):  # Printable ASCII
        char = chr(ascii_code)
        ids = tokenizer.encode(char, add_special_tokens=False)
        if ids and len(ids) == 1:
            token_id = ids[0]
            ascii_token_map[token_id] = ascii_code
            token_to_ascii[char] = token_id
            if verbose and ascii_code < 96:  # ASCII codes 32-95 fit in 6 bits (0-63) after subtracting 32
                print(f"Mapped ASCII {ascii_code} ('{char}') to token ID {token_id}")
    
    # Add common digraphs, trigraphs that might be represented as single tokens
    common_substrings = [" ", " a", " the", "ing", "ed", "er", "'s", "the", "and", "of", "to", "in"]
    for text in common_substrings:
        ids = tokenizer.encode(text, add_special_tokens=False)
        if ids and len(ids) == 1:
            token_id = ids[0]
            token_to_ascii[text] = token_id
            if verbose:
                print(f"Mapped text '{text}' to token ID {token_id}")
            
    return ascii_token_map, token_to_ascii

def compress_text(file_path, output_path, top_k=64, verbose=False):
    """
    Compress text using LLM predictability.
    For tokens predicted within the top_k (here 64), encode their rank.
    Otherwise, encode the token explicitly (as a raw token) using our custom binary format.
    
    Additionally, if a token corresponds to a common ASCII character (from 32 to 126),
    and if its ASCII code is between 32 and 95 (so that ascii_code-32 fits in 6 bits),
    we encode it as a raw token with value = (ascii_code - 32).
    """
    # Load model and tokenizer.
    print("Loading tokenizer and model...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    
    vocab_size = tokenizer.vocab_size
    print(f"Tokenizer vocabulary size: {vocab_size}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print(f"Using device: {device}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Tokenize the text
    print("Tokenizing input text...")
    tokens = tokenizer.encode(text)
    print(f"Text tokenized into {len(tokens)} tokens")
    
    # Safety check – ensure all tokens are within vocabulary range.
    safe_tokens = []
    for i, token_id in enumerate(tokens):
        if token_id >= vocab_size:
            print(f"Warning: Token ID {token_id} at position {i} exceeds vocabulary size. Using UNK token.")
            safe_tokens.append(0)
        else:
            safe_tokens.append(token_id)
    tokens = safe_tokens
    
    # Build ASCII mapping for characters and common substrings
    ascii_token_map, token_to_ascii = build_ascii_mapping(tokenizer, verbose)
    
    # Print some sample token-to-text mappings for reference
    if verbose:
        print("\nExamining some tokens to see what they represent:")
        sample_token_ids = tokens[:20] + tokens[len(tokens)//2:len(tokens)//2+20]
        for token_id in sample_token_ids:
            token_text = tokenizer.decode([token_id])
            in_ascii_map = token_id in ascii_token_map
            ascii_val = ascii_token_map.get(token_id, -1)
            print(f"Token ID {token_id} -> '{token_text}' {'(ASCII: ' + str(ascii_val) + ')' if in_ascii_map else ''}")
    
    compressed_bytes = bytearray()
    
    # Print stats as we process
    stats = {"rank_tokens": 0, "ascii_tokens": 0, "explicit_tokens": 0}
    
    print("\nCompressing tokens...")
    # Create a progress bar for the compression process
    for i, token_id in tqdm(enumerate(tokens), total=len(tokens), desc="Compressing", unit="token", disable=verbose):
        # Check if this token corresponds to an ASCII character first
        # ASCII tokens get priority over both rank and explicit tokens for better compression
        if token_id in ascii_token_map:
            ascii_val = ascii_token_map[token_id]
            # Only if it fits in one byte (i.e. ascii_val between 32 and 95)
            if 32 <= ascii_val < 96:
                # Store as raw token with value = ascii_val - 32
                compressed_bytes.extend(encode_raw_token(ascii_val - 32))
                stats["ascii_tokens"] += 1
                if verbose and (i % 100 == 0 or i < 5):
                    print(f"Token {i}: ASCII raw token, char '{chr(ascii_val)}' ({ascii_val})")
                continue
        
        # For the very first token or when ascii encoding is not possible
        if i == 0:
            # First token has to be explicit since there's no context
            compressed_bytes.extend(encode_raw_token(token_id))
            stats["explicit_tokens"] += 1
            if verbose:
                print(f"Token {i}: Explicit raw token ID {token_id} -> '{tokenizer.decode([token_id])}'")
            continue
        
        # For subsequent tokens, use previous tokens as context.
        try:
            context = tokens[:i]
            context_tensor = torch.tensor([context], dtype=torch.long, device=device)
            with torch.no_grad():
                outputs = model(context_tensor)
                logits = outputs.logits[:, -1, :]
            topk_indices = torch.topk(logits, k=min(top_k, vocab_size), dim=-1).indices.squeeze().tolist()
            
            if token_id in topk_indices:
                rank = topk_indices.index(token_id)
                compressed_bytes.extend(encode_rank_token(rank))
                stats["rank_tokens"] += 1
                if verbose and (i % 100 == 0 or i < 5):
                    token_text = tokenizer.decode([token_id])
                    print(f"Token {i}: Rank {rank} -> '{token_text}'")
            else:
                # Not in top predictions: encode explicitly.
                compressed_bytes.extend(encode_raw_token(token_id))
                stats["explicit_tokens"] += 1
                if verbose and (i % 100 == 0 or i < 5):
                    token_text = tokenizer.decode([token_id])
                    print(f"Token {i}: Explicit raw token ID {token_id} -> '{token_text}'")
        except Exception as e:
            if verbose:
                print(f"Error at token {i}: {e}")
            compressed_bytes.extend(encode_raw_token(token_id))
            stats["explicit_tokens"] += 1
    
    # Calculate and print encoding stats
    total_tokens = len(tokens)
    print("\nCompression statistics:")
    print(f"- ASCII tokens: {stats['ascii_tokens']} ({stats['ascii_tokens']/total_tokens*100:.2f}%)")
    print(f"- Rank tokens: {stats['rank_tokens']} ({stats['rank_tokens']/total_tokens*100:.2f}%)")
    print(f"- Explicit tokens: {stats['explicit_tokens']} ({stats['explicit_tokens']/total_tokens*100:.2f}%)")
    
    print(f"Writing {len(compressed_bytes)} bytes to output file...")
    with open(output_path, 'wb') as out_f:
        out_f.write(compressed_bytes)
    print(f"Compressed output written to {output_path}")
    
    # Calculate estimated savings
    if verbose:
        total_bytes_without_ranking = sum([
            len(encode_raw_token(token_id)) for token_id in tokens
        ])
        savings_from_ranking = total_bytes_without_ranking - len(compressed_bytes)
        print(f"Estimated space savings: {savings_from_ranking} bytes ({savings_from_ranking/total_bytes_without_ranking*100:.2f}%)")
    
    return compressed_bytes

def main():
    parser = argparse.ArgumentParser(
        description="Compress a text file using LLM predictability and custom binary encoding."
    )
    parser.add_argument("input_file", help="Path to the input text file")
    parser.add_argument("--output", "-o", help="Path for the output compressed file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed token information")
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output if args.output else "compressed.bin"
    compress_text(input_file, output_file, top_k=64, verbose=args.verbose)

    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)
    ratio = original_size / compressed_size if compressed_size > 0 else 0
    print(f"Compression ratio: {ratio:.2f}x ({original_size} bytes / {compressed_size} bytes)")
    print(f"Space savings: {(1-1/ratio)*100:.2f}%")


if __name__ == "__main__":
    main()
