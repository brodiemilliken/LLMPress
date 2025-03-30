def compare_tokens(encoded_tokens, decoded_tokens):
    """
    Compare encoded and decoded tokens to check if they're identical.
    
    Args:
        encoded_tokens (list): List of encoded tokens
        decoded_tokens (list): List of decoded tokens
        
    Returns:
        tuple: (bool, list) - Whether they're identical and a list of differences
    """
    if len(encoded_tokens) != len(decoded_tokens):
        return False, [(f"Length mismatch: encoded({len(encoded_tokens)}) != decoded({len(decoded_tokens)})", None, None)]
    
    differences = []
    
    for i, (e_token, d_token) in enumerate(zip(encoded_tokens, decoded_tokens)):
        if e_token != d_token:
            differences.append((i, e_token, d_token))
    
    return len(differences) == 0, differences

def save_debug_info(tokens, file_path, token_type="encoded"):
    """
    Save token information for debugging purposes.
    
    Args:
        tokens (list): List of tokens to save
        file_path (str): Path to save tokens to
        token_type (str): Type of tokens (encoded or decoded)
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"=== {token_type.capitalize()} Tokens ===\n\n")
        
        if token_type == "encoded" or token_type == "decoded":
            # For encoded/decoded tokens with type and value
            f.write("Index | Type | Value\n")
            f.write("----- | ---- | -----\n")
            for i, token in enumerate(tokens):
                token_type = token[0]
                token_value = token[1]
                type_str = "Rank" if token_type == "r" else "Expl"
                f.write(f"{i:5d} | {type_str:4s} | {token_value}\n")
                
            # Add statistics for encoded tokens
            if token_type == "encoded":
                rank_tokens = sum(1 for t in tokens if t[0] == "r")
                explicit_tokens = sum(1 for t in tokens if t[0] == "e")
                f.write(f"\nSummary:\n")
                f.write(f"- Total tokens: {len(tokens)}\n")
                f.write(f"- Rank tokens: {rank_tokens} ({rank_tokens/len(tokens)*100:.2f}%)\n")
                f.write(f"- Explicit tokens: {explicit_tokens} ({explicit_tokens/len(tokens)*100:.2f}%)\n")

def save_token_comparison(encoded_tokens, decoded_tokens, file_path):
    """
    Save token comparison information for debugging.
    
    Args:
        encoded_tokens (list): List of encoded tokens
        decoded_tokens (list): List of decoded tokens
        file_path (str): Path to save comparison to
    """
    tokens_match, differences = compare_tokens(encoded_tokens, decoded_tokens)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("=== Token Comparison ===\n\n")
        
        if tokens_match:
            f.write("✅ Encoded and decoded tokens are identical!\n")
            f.write(f"Total tokens: {len(encoded_tokens)}\n")
        else:
            f.write("❌ Encoded and decoded tokens have differences!\n\n")
            
            if isinstance(differences[0][0], str):
                # This is a length mismatch error message
                f.write(f"{differences[0][0]}\n")
            else:
                f.write("Index | Encoded Token | Decoded Token\n")
                f.write("----- | ------------- | -------------\n")
                
                for idx, e_token, d_token in differences:
                    e_type = "Rank" if e_token[0] == "r" else "Expl"
                    d_type = "Rank" if d_token[0] == "r" else "Expl"
                    f.write(f"{idx:5d} | {e_type}({e_token[1]}) | {d_type}({d_token[1]})\n")
                
                f.write(f"\nTotal differences: {len(differences)} out of {len(encoded_tokens)} tokens ({len(differences)/len(encoded_tokens)*100:.2f}%)\n")