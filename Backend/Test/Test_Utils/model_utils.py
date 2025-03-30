import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Import the APIClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))) 
from Backend.APIClient import APIClient

def initialize_model(model_name="gpt2", use_api=False, api_url="http://localhost:8000"):
    """
    Initialize a model instance - either direct GPT2 or API client.
    
    Args:
        model_name (str): The name of the model to initialize
        use_api (bool): Whether to use the API client
        api_url (str): URL for the API server
        
    Returns:
        The initialized model or API client
    """
    if use_api:
        print(f"Connecting to AI API at '{api_url}'...")
        client = APIClient(base_url=api_url)
        # Just return the client, error handling happens inside APIClient
        return client
    else:
        print(f"Failed to connect to API at '{api_url}'")
        #print(f"Initializing model '{model_name}'...")
        # Import here to avoid circular imports
        #from AI.ChatGPT2 import GPT2
        #return GPT2(model_name=model_name)