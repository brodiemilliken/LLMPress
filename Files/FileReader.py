class FileReader:
    """
    A class for managing file reading operations.
    Provides methods to read file contents.
    """
    
    def __init__(self):
        """Initialize the FileReader."""
        pass
    
    def read_file_to_string(self, file_path):
        """
        Reads a file and returns its contents as a string.
        
        Args:
            file_path (str): Path to the file to be read
            
        Returns:
            str: The contents of the file as a string
            
        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be accessed due to permissions
            Exception: For other reading errors
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
            raise
        except PermissionError:
            print(f"Error: Permission denied when trying to access {file_path}")
            raise
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            raise