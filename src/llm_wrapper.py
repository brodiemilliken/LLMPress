import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class LLMWrapper:
    def __init__(self, model_name='gpt2', top_k=5):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.top_k = top_k

    def get_top_k_ranks(self, input_text):
        inputs = self.tokenizer.encode(input_text, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(inputs)
            logits = outputs.logits[:, -1, :]
            top_k_logits, top_k_indices = torch.topk(logits, self.top_k)

        top_k_tokens = self.tokenizer.convert_ids_to_tokens(top_k_indices[0])
        top_k_scores = torch.softmax(top_k_logits, dim=-1).squeeze().tolist()

        return list(zip(top_k_tokens, top_k_scores))

    def encode(self, text):
        return self.tokenizer.encode(text, return_tensors='pt')

    def decode(self, token_ids):
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)