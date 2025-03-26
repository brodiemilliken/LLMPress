from AI.ChatGPT2 import GPT2
from Compression import Tokenize

# Create an instance of the GPT2 class
model = GPT2(model_name="gpt2")

# Now use the instance with Tokenize
text = "Hello World! This is a test"
tokens = Tokenize.encode_text(text, model, k=256)
print(tokens)