import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from ai_interface import AIPredictorInterface

class GPT2NextWordPredictor(AIPredictorInterface):
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
        
    def predict_next_words(self, text: str, k: int) -> list:
        """
        Predict the top K most likely next words given the input text.
        
        Args:
            text (str): The input text prompt
            k (int): Number of top predictions to return
            
        Returns:
            list: Top K predictions with their ranks
        """
        # Encode the text
        inputs = self.tokenizer.encode(text, return_tensors="pt")
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(inputs)
            predictions = outputs.logits
        
        # Get the predictions for the next token
        next_token_logits = predictions[0, -1, :]
        
        # Get the top k tokens
        top_k_values, top_k_indices = torch.topk(next_token_logits, k)
        
        # Get token strings
        top_k_tokens = [self.tokenizer.decode([idx]) for idx in top_k_indices]
            
        return top_k_tokens

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
        return tokens

    def get_word_from_tokens(self, token: int or list) -> str:
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

# Example usage
if __name__ == "__main__":
    # Initialize the predictor
    predictor = GPT2NextWordPredictor("gpt2")  # You can change to larger models if needed
    
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

    word = predictor.get_word_from_token(tokens)
    print(f"Word: '{word}'")
