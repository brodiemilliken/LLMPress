import os
import filecmp

def create_output_dirs(output_dir, debug=False):
    """
    Create output directories for compressed and decompressed files.
    
    Args:
        output_dir (str): Base output directory
        debug (bool): Whether to create debug directory
        
    Returns:
        tuple: (compressed_dir, results_dir, debug_dir)
    """
    compressed_dir = os.path.join(output_dir, "Compressed")
    results_dir = os.path.join(output_dir, "Results")
    debug_dir = None
    
    os.makedirs(compressed_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    if debug:
        debug_dir = os.path.join(output_dir, "Debug")
        os.makedirs(debug_dir, exist_ok=True)
        
    return compressed_dir, results_dir, debug_dir

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