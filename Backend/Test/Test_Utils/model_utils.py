import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from AI.ChatGPT2 import GPT2

def initialize_model(model_name="gpt2"):
    """
    Initialize a GPT2 model with the given name.
    
    Args:
        model_name (str): The name of the model to initialize
        
    Returns:
        GPT2: The initialized model
    """
    print(f"Initializing model '{model_name}'...")
    return GPT2(model_name=model_name)