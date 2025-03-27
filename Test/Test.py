import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI.ChatGPT2 import GPT2
from Compression import Tokenize, Encoder
from Decompression import Detokenize, Decoder

# Create an instance of the GPT2 class
model = GPT2(model_name="gpt2")

# Now use the instance with Tokenize
k = 64
with open("Test/sample.txt", "r", encoding="utf-8") as file:
    text = file.read()

tokens = Tokenize.encode_text(text, model, k)
bin = Encoder.encode_tokens(tokens)

with open("Test/sample.bin", "wb") as file:
    file.write(bin)

original_file_size = os.path.getsize("Test/sample.txt")
bin_file_size = os.path.getsize("Test/sample.bin")

print(f"Original file size: {original_file_size} bytes")
print(f"Binary file size: {bin_file_size} bytes")

tokens = Decoder.decode_bytes(bin)
text = Detokenize.decode_tokens(tokens, model, k)

print(text)
print("Tokens:", tokens)