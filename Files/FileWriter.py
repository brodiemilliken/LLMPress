class FileWriter:
    """
    A class for managing file writing operations.
    Provides methods to open a file, write to it, and close it.
    """
    
    def __init__(self):
        """Initialize the FileWriter with no open file."""
        self.file = None
        self.file_path = None
    
    def open_file_for_writing(self, file_path, mode='w'):
        """
        Opens a file for writing.
        
        Args:
            file_path (str): Path to the file to write to
            mode (str): File opening mode ('w' for write, 'a' for append)
                        Default is 'w' which overwrites existing content
        
        Returns:
            bool: True if file was opened successfully, False otherwise
            
        Raises:
            ValueError: If the file is already open
            PermissionError: If the file cannot be accessed due to permissions
        """
        if self.file is not None:
            raise ValueError(f"A file is already open: {self.file_path}")
            
        try:
            self.file = open(file_path, mode, encoding='utf-8')
            self.file_path = file_path
            return True
        except PermissionError:
            print(f"Error: Permission denied when trying to access {file_path}")
            raise
        except Exception as e:
            print(f"Error opening file {file_path}: {str(e)}")
            raise
    
    def write_to_file(self, content):
        """
        Writes content to the currently open file.
        
        Args:
            content (str): The content to write to the file
            
        Returns:
            bool: True if content was written successfully
            
        Raises:
            ValueError: If no file is currently open
        """
        if self.file is None:
            raise ValueError("No file is currently open for writing")
            
        try:
            self.file.write(content)
            return True
        except Exception as e:
            print(f"Error writing to file {self.file_path}: {str(e)}")
            raise
    
    def close_file(self):
        """
        Closes the currently open file.
        
        Returns:
            bool: True if file was closed successfully, False if no file was open
        """
        if self.file is None:
            return False
            
        try:
            self.file.close()
            self.file = None
            self.file_path = None
            return True
        except Exception as e:
            print(f"Error closing file {self.file_path}: {str(e)}")
            raise