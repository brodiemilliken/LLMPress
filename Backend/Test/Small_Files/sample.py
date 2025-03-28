"""
This is a sample Python file for testing purposes.
It contains a simple function and a loop to generate output.
"""

def greet(name: str) -> str:
    """
    Returns a greeting message for the given name.
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    for name in names:
        print(greet(name))