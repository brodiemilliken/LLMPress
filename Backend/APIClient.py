import sys
import os
import requests
from typing import List, Tuple

# Make sure the Backend directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

class APIClient:
    """Client for connecting to the LLMPress API with simplified direct requests."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Test connection
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print(f"Successfully connected to AI API at {self.base_url}")
            else:
                print(f"Warning: API responded with status code {response.status_code}")
        except Exception as e:
            print(f"Warning: Could not connect to API at {self.base_url}: {str(e)}")
    
    def tokenize(self, text):
        """
        Tokenize text using a direct API call.
        
        Args:
            text: The text to tokenize.
            
        Returns:
            The tokenized result (list of token tuples).
        """
        try:
            response = self.session.post(
                f"{self.base_url}/tokenize",
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in tokenize call: {str(e)}")
            raise e
    
    def detokenize(self, tokens):
        """
        Detokenize tokens using a direct API call.
        
        Args:
            tokens: The tokens to detokenize.
            
        Returns:
            The detokenized text.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/detokenize",
                json={"tokens": tokens}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in detokenize call: {str(e)}")
            raise e

# Example usage
if __name__ == "__main__":
    client = APIClient()
    
    # Simple tokenization example
    text = "This is an example of tokenization."
    print("\nTokenizing text:")
    tokens = client.tokenize(text)
    print("Tokenized result:", tokens)
    
    # Simple detokenization example
    print("\nDetokenizing tokens:")
    result = client.detokenize(tokens)
    print("Detokenized result:", result)


