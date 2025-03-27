import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from typing import Union, List
from .ai_interface import AI

class GPT2(AI):
    def __init__(self, model_name="gpt2"):
        """
        Initialize the GPT-2 model and tokenizer.
        
        Args:
            model_name (str): The GPT-2 model to use. Options include:
                "gpt2" (117M parameters), "gpt2-medium" (345M parameters),
                "gpt2-large" (774M parameters), "gpt2-xl" (1.5B parameters)
        """
        print(f"Loading {model_name} model and tokenizer...")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.eval()  # Set model to evaluation mode
        print("Model loaded successfully!")
        
    def list_rank_tokens(self, tokens: list, k: int) -> list:
        """
        Predict the top K most likely next tokens given the input token sequence.
        
        Args:
            tokens (list): The input token sequence
            k (int): Number of top predictions to return
            
        Returns:
            list: Top K token IDs sorted by probability
        """
        # Convert the token list to a tensor
        inputs = torch.tensor([tokens], dtype=torch.long)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(inputs)
            predictions = outputs.logits
        
        # Get the predictions for the next token
        next_token_logits = predictions[0, -1, :]
        
        # Get the top k tokens
        top_k_values, top_k_indices = torch.topk(next_token_logits, k)
        
        # Return the token indices
        return top_k_indices.tolist()

    def get_tokens_for_word(self, word: str) -> list:
        """
        Get the token(s) corresponding to a given word.

        Args:
            word (str): The input word to tokenize.

        Returns:
            list: A list of token IDs corresponding to the word.
        """
        # Tokenize the word
        tokens = self.tokenizer.encode(word, add_special_tokens=True)
        tokens = [int(token) for token in tokens]
        return tokens
        
    def get_word_from_tokens(self, token: Union[int, List[int]]) -> str:
        """
        Get the word(s) corresponding to a given token or list of tokens.

        Args:
            token (int or list): The input token ID or list of token IDs.

        Returns:
            str: The decoded word(s) corresponding to the token(s).
        """
        # Decode the token(s) into a word or phrase
        if isinstance(token, list):
            word = self.tokenizer.decode(token, clean_up_tokenization_spaces=False)
        else:
            word = self.tokenizer.decode([token], clean_up_tokenization_spaces=False)
        return word

    def tokenize(self, text: str) -> list:
        """
        Convert a text string into a list of token IDs.

        Args:
            text (str): The input text to tokenize.

        Returns:
            list: A list of token IDs corresponding to the text.
        """
        # Tokenize the text
        return self.tokenizer.encode(text, add_special_tokens=True)
    
    def detokenize(self, tokens):
        """
        Convert a list of token IDs into a text string

        Args:
            tokens (list[int]): The input list of token IDs.

        Returns:
            str: The decoded text string corresponding to the token IDs.
        """
        return self.tokenizer.decode(tokens, skip_special_tokens=True)

# Example usage
if __name__ == "__main__":
    # Initialize the predictor
    predictor = GPT2("gpt2")  # You can change to larger models if needed
    
    # Example text
    example_text = "The quick brown fox jumps over the lazy"
    
    # Get top 5 predictions
    predictions = predictor.predict_next_words(example_text, k=8)
    
    # Display results
    print(f"\nInput text: '{example_text}'")
    print("Top predicted next words:")
    for i, pred in enumerate(predictions, 1):
        print(f"{i}. {pred}")
    
    # Example usage of get_tokens_for_word
    word = "Hello"
    tokens = predictor.get_tokens_for_word(word)
    print(f"\nWord: '{word}'")
    print(f"Tokens: {tokens}")

    word = predictor.get_word_from_tokens(tokens)
    print(f"Word: '{word}'")
