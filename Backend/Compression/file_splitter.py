import os
import re
import logging
from ..exceptions import FileOperationError, ChunkingError

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LLMPress.FileSplitter')

# Common semantic delimiters based on file type
DELIMITER_PATTERNS = {
    # General text delimiters (apply to all formats)
    'general': [
        r'\n\n',                   # Double newline (paragraph break)
        r'\n---+\n',               # Horizontal rule
        r'\n\*\*\*+\n',            # Asterisk horizontal rule
        r'\n___+\n',               # Underscore horizontal rule
    ],
    
    # Programming languages
    'python': [
        r'def\s+\w+\(.*?\):\s*(?:\n\s+.*?)?(?=\n\n|\Z)',  # Function definition (non-greedy)
        r'class\s+\w+.*?:\s*(?:\n\s+.*?)?(?=\n\n|\Z)',    # Class definition (non-greedy)
        r'""".*?"""',              # Triple-quote docstring (non-greedy)
        r"'''.*?'''",              # Triple-quote docstring (single quotes)
        r'#\s*[-=]{3,}.*?\n',      # Comment separator
        r'if\s+.*?:\s*(?:\n\s+.*?)?(?=\n\n|\Z)',         # if block (non-greedy)
        r'for\s+.*?:\s*(?:\n\s+.*?)?(?=\n\n|\Z)',        # for loop (non-greedy)
        r'while\s+.*?:\s*(?:\n\s+.*?)?(?=\n\n|\Z)',      # while loop (non-greedy)
    ],
    
    'java': [
        r'}\s*\n',                 # End of block (method, class, etc.)
        r'/\*\*.*?\*/\s*\n',       # End of JavaDoc comment (non-greedy)
        r'//\s*[-=]{3,}.*?\n',     # Comment separator
        r'public\s+(?:class|interface|enum)\s+\w+',  # Class/interface declaration
        r'(?:public|private|protected)(?:\s+static)?\s+\w+\s+\w+\([^)]*\)',  # Method signature
    ],
    
    # Markup languages
    'html': [
        r'</(?:div|section|article|header|footer|nav|main|aside)>',  # End of block elements
        r'</h[1-6]>',              # End of heading
        r'</p>\s*\n',              # End of paragraph
        r'</(?:ul|ol)>',           # End of list
        r'</table>',               # End of table
        r'</form>',                # End of form
        r'<!--.*?-->',             # HTML comment
    ],
    
    'markdown': [
        r'^#{1,6}\s+.*$',          # Markdown heading
        r'^\s*[-*+]\s+',           # Unordered list item
        r'^\s*\d+\.\s+',           # Ordered list item
        r'^\s*>\s+',               # Blockquote
        r'```.*?```',              # Code block
    ],
    
    # Data formats
    'json': [
        r'},\s*\n',                # End of JSON object
        r'\],\s*\n',               # End of JSON array
    ],
    
    'xml': [
        r'</[^>]+>\s*\n',          # End of XML tag
    ]
}

def split_text(text, min_chunk_size=500, max_chunk_size=2000, file_type=None):
    """
    Split text into chunks based on semantic delimiters.
    
    Args:
        text (str): The input text to split
        min_chunk_size (int): Minimum size of each chunk
        max_chunk_size (int): Maximum size of each chunk
        file_type (str, optional): Specific file type to use delimiters for
        
    Returns:
        list: List of text chunks with delimiters preserved
        
    Raises:
        ChunkingError: If there's an error during text chunking
    """
    try:
        # Use a simpler approach: first try to split by paragraphs
        chunks = []
        current_chunk = ""
        
        # First, split by paragraph or reasonable delimiters
        simple_pattern = r'\n\n|\n[-=*]{3,}\n'
        
        # Start with a simple split by paragraphs
        segments = re.split(f'({simple_pattern})', text)
        
        for i in range(0, len(segments), 2):
            segment = segments[i]
            delimiter = segments[i+1] if i+1 < len(segments) else ""
            
            proposed_addition = segment + delimiter
            
            # If adding this would exceed max size and we already have content
            if len(current_chunk) + len(proposed_addition) > max_chunk_size and len(current_chunk) >= min_chunk_size:
                chunks.append(current_chunk)
                current_chunk = proposed_addition
            else:
                current_chunk += proposed_addition
                
                # If we've accumulated enough and hit a natural break
                if len(current_chunk) >= min_chunk_size and delimiter:
                    chunks.append(current_chunk)
                    current_chunk = ""
        
        # Handle any leftover content
        if current_chunk:
            # If the current chunk is too small and we have previous chunks, 
            # merge with the last chunk if possible
            if len(current_chunk) < min_chunk_size and chunks:
                last_chunk = chunks.pop()
                merged = last_chunk + current_chunk
                
                # Only merge if it doesn't exceed max_chunk_size too much
                if len(merged) <= max_chunk_size * 1.5:
                    chunks.append(merged)
                else:
                    chunks.append(last_chunk)
                    chunks.append(current_chunk)
            else:
                chunks.append(current_chunk)
        
        # Check if we need to further split large chunks
        i = 0
        while i < len(chunks):
            if len(chunks[i]) > max_chunk_size * 1.5:
                # Use a more aggressive splitting approach for oversized chunks
                large_chunk = chunks[i]
                
                # Try to find line breaks or sentences to split on
                simple_breaks = re.split(r'(\n|(?<=[.!?])\s+)', large_chunk)
                
                new_chunk = ""
                sub_chunks = []
                
                for j in range(0, len(simple_breaks), 2):
                    text_part = simple_breaks[j]
                    break_part = simple_breaks[j+1] if j+1 < len(simple_breaks) else ""
                    
                    if len(new_chunk) + len(text_part) + len(break_part) > max_chunk_size and len(new_chunk) >= min_chunk_size:
                        sub_chunks.append(new_chunk)
                        new_chunk = text_part + break_part
                    else:
                        new_chunk += text_part + break_part
                
                if new_chunk:
                    sub_chunks.append(new_chunk)
                
                # Replace the large chunk with the sub-chunks
                chunks[i:i+1] = sub_chunks
                i += len(sub_chunks)
            else:
                i += 1
        
        # Verify integrity
        reconstructed = ''.join(chunks)
        if len(reconstructed) != len(text):
            logger.warning(f"Chunking integrity issue: Original {len(text)} bytes, Reconstructed {len(reconstructed)} bytes")
            # If we've lost data, fall back to a simpler chunking method
            # that just divides the text into equal parts
            chunks = []
            chunk_size = max_chunk_size
            
            for i in range(0, len(text), chunk_size):
                chunks.append(text[i:min(i + chunk_size, len(text))])
                
            logger.info(f"Fallback chunking: Created {len(chunks)} equal-sized chunks")
        else:
            logger.info(f"Successfully chunked text into {len(chunks)} chunks")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error during text chunking: {str(e)}", exc_info=True)
        raise ChunkingError(f"Failed to chunk text: {str(e)}")

def detect_file_type(file_path):
    """
    Detect file type based on extension.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Detected file type or None
    """
    ext_map = {
        '.py': 'python',
        '.java': 'java', 
        '.js': 'java',  # JavaScript uses similar block structure
        '.html': 'html',
        '.htm': 'html',
        '.md': 'markdown',
        '.json': 'json',
        '.xml': 'xml',
        '.txt': 'general'
    }
    
    ext = os.path.splitext(file_path)[1].lower()
    if not ext and '.' in file_path:
        # Handle cases where os.path.splitext doesn't work as expected
        ext = '.' + file_path.lower().split('.')[-1]
    
    return ext_map.get(ext, 'general')

def chunk_file(file_path, min_chunk_size=500, max_chunk_size=2000):
    """
    Split a file's content into chunks.
    
    Args:
        file_path (str): Path to the file to chunk
        min_chunk_size (int): Minimum size of each chunk
        max_chunk_size (int): Maximum size of each chunk
        
    Returns:
        list: List of text chunks
        
    Raises:
        FileOperationError: If there's an error reading the file
        ChunkingError: If there's an error during text chunking
    """
    logger.info(f"Chunking file: {file_path}")
    
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        raise FileOperationError(error_msg)
        
    if not os.path.isfile(file_path):
        error_msg = f"Not a file: {file_path}"
        logger.error(error_msg)
        raise FileOperationError(error_msg)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 decoding failed for {file_path}, trying latin-1")
        try:
            # Fall back to latin-1 if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise FileOperationError(error_msg)
    except Exception as e:
        error_msg = f"Failed to read file {file_path}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise FileOperationError(error_msg)
    
    file_type = detect_file_type(file_path)
    logger.info(f"Detected file type: {file_type} for {file_path}")
    
    try:
        chunks = split_text(content, min_chunk_size, max_chunk_size, file_type)
        logger.info(f"Successfully chunked {file_path} into {len(chunks)} chunks")
        return chunks
    except ChunkingError:
        # Re-raise the original ChunkingError
        raise
    except Exception as e:
        error_msg = f"Failed to chunk file {file_path}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ChunkingError(error_msg)