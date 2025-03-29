# Add to your existing imports:
import sys
import os

# Make sure the Backend directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Define the APIClient class inline to avoid dependencies
class APIClient:
    """Simple client for connecting to the LLMPress API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        import requests
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
        try:
            import json
            response = self.session.post(
                f"{self.base_url}/tokenize",
                json={"text": text},
                timeout=10  # Add timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in API call to tokenize: {str(e)}")
            raise e
    
    def detokenize(self, tokens):
        import json
        response = self.session.post(
            f"{self.base_url}/detokenize",
            json={"tokens": tokens}
        )
        response.raise_for_status()
        return response.json()
    
    def list_rank_tokens(self, tokens, k=5):
        import json
        response = self.session.post(
            f"{self.base_url}/list_rank_tokens",
            json={"tokens": tokens, "k": k}
        )
        response.raise_for_status()
        return response.json()

