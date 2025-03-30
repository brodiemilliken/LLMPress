import requests
import json
import time

def test_regular_endpoints():
    """Test the regular endpoints."""
    print("Testing regular endpoints...")
    
    # Test endpoint - should be GET
    response = requests.get("http://localhost:8000/test")
    print(f"Test endpoint - Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Regular tokenize endpoint
    response = requests.post(
        "http://localhost:8000/tokenize",
        json={"text": "This is a simple test message."}
    )
    print(f"Regular tokenize - Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Got {len(result)} tokens: {result}")
    else:
        print(f"Error: {response.text}")
        
    # Regular detokenize endpoint with sample tokens
    # Format is now [type, value] list rather than simple integers
    tokens = [["e", 1212], ["r", 0], ["r", 0], ["r", 10], ["r", 10], ["e", 3275], ["r", 1]]
    response = requests.post(
        "http://localhost:8000/detokenize",
        json={"tokens": tokens}
    )
    print(f"\nRegular detokenize - Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Detokenized result: {result}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    # Test the regular endpoints
    test_regular_endpoints()