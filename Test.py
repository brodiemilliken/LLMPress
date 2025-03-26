from AI.ChatGPT2 import GPT2
from Compression import Tokenize
from Decompression import Detokenize
# Create an instance of the GPT2 class
model = GPT2(model_name="gpt2")

# Now use the instance with Tokenize
k = 256
text = "Hello World! This is a test"
tokens = Tokenize.encode_text(text, model, k)
print(tokens)
text = Detokenize.decode_tokens(tokens, model, k)
print(text)