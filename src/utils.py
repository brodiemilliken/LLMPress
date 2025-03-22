import os
import torch
import importlib.util
import sys

def encode_tokens(text, tokenizer):
    """Encode text to token IDs using the provided tokenizer"""
    tokens = tokenizer.encode(text, add_special_tokens=False)
    if not isinstance(tokens, torch.Tensor):
        tokens = torch.tensor([tokens])
    return tokens

def decode_tokens(tokens, tokenizer):
    """Decode token IDs to text using the provided tokenizer"""
    if isinstance(tokens, torch.Tensor):
        tokens = tokens.tolist()
    if isinstance(tokens, int):
        tokens = [tokens]
    elif not isinstance(tokens, list):
        tokens = [tokens]
    return tokenizer.decode(tokens, skip_special_tokens=True)

def get_tokenizer(model_name='gpt2'):
    """Get a tokenizer, with fallback to minimal implementation if Rust tokenizer fails"""
    # Check if tokenizers is available
    tokenizers_spec = importlib.util.find_spec("tokenizers")
    has_tokenizers = tokenizers_spec is not None
    
    try:
        # Try the standard route first
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(model_name)
    except (ImportError, ModuleNotFoundError) as e:
        # The import error could be for multiple reasons
        error_msg = str(e).lower()
        
        if any(x in error_msg for x in ['tokenizers', 'rust', 'onig']):
            print("Warning: Issue with tokenizers package. Using fallback.")
        else:
            # If it's a different issue with transformers
            print(f"Warning: Could not import AutoTokenizer: {e}")
        
        # Try using our minimal tokenizer
        try:
            minimal_tokenizer_path = os.path.join(os.path.dirname(__file__), "minimal_tokenizer.py")
            if os.path.exists(minimal_tokenizer_path):
                # First try direct import
                try:
                    from minimal_tokenizer import MinimalTokenizer
                except ImportError:
                    # If direct import fails, try loading as module from file
                    spec = importlib.util.spec_from_file_location("minimal_tokenizer", minimal_tokenizer_path)
                    minimal_tokenizer = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(minimal_tokenizer)
                    MinimalTokenizer = minimal_tokenizer.MinimalTokenizer
                
                # Create tokenizer instance
                tokenizer = MinimalTokenizer()
                
                # Check if we have a saved model
                saved_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                        "models", f"{model_name}_minimal_tokenizer")
                if os.path.exists(os.path.join(saved_dir, "vocab.json")):
                    return tokenizer.from_pretrained(saved_dir)
                return tokenizer
        except Exception as e:
            print(f"Warning: Minimal tokenizer also failed: {e}")
        
        # Last resort - create an extremely basic tokenizer
        class EmergencyTokenizer:
            def encode(self, text, add_special_tokens=False):
                return [ord(c) for c in text]
                
            def decode(self, tokens, skip_special_tokens=True):
                return ''.join([chr(t) if isinstance(t, int) else chr(t.item()) 
                              if hasattr(t, 'item') else '?' for t in tokens])
        
        print("WARNING: Using emergency character-level tokenizer. Results may be poor.")
        return EmergencyTokenizer()

def bit_conversion(value):
    return bin(value)[2:]

def int_from_bits(bits):
    return int(bits, 2)

def save_to_file(data, file_path):
    with open(file_path, 'w') as f:
        f.write(data)

def load_from_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

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

def calculate_compression_ratio(compressed_file, decompressed_text):
    """Calculate and return compression ratio information."""
    compressed_size = os.path.getsize(compressed_file)
    decompressed_size = len(decompressed_text.encode('utf-8'))
    
    if decompressed_size == 0:
        return "Unable to calculate ratio (decompressed size is 0)"
    
    ratio = compressed_size / decompressed_size
    return {
        'ratio': ratio,
        'compressed_size': compressed_size,
        'decompressed_size': decompressed_size,
        'summary': f"Compression ratio: {ratio:.2f} ({compressed_size} bytes / {decompressed_size} bytes)"
    }

def validate_compressed_file(file_path):
    """Validate a compressed file format before decompression."""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
            
        if not lines:
            return False, "File is empty"
            
        # Each line should contain an integer
        for i, line in enumerate(lines):
            try:
                int(line)
            except ValueError:
                return False, f"Invalid token value at line {i+1}: {line}"
                    
        return True, "File format is valid"
    
    except Exception as e:
        return False, f"Error validating file: {str(e)}"