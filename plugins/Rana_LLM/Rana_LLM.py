
from pluginInterface import LLMPluginInterface
import gradio as gr
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class RanaLLM(LLMPluginInterface):
    context_length = 2048
    def init(self):
        # Check if CUDA is available and set the device accordingly
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"torch.cuda.is_available() {torch.cuda.is_available()}")

        self.tokenizer = AutoTokenizer.from_pretrained("xiaoheiqaq/Rana")
        print(f"Loading Rana...")
        self.model = AutoModelForCausalLM.from_pretrained("xiaoheiqaq/Rana").to(self.device)
        # Set the model to evaluation mode
        self.model.eval()

    def predict(self, message, history, system_prompt):
        messages = f"<|user|>{system_prompt}<|endoftext|>"
        for entry in history:
            user, ai = entry
            messages += f"<|user|>{user}<|assistant|>{ai}"

        # Prepare an input prompt
        messages = f"<|user|>{message}<|assistant|>"
        # Encode the input prompt
        input_ids = self.tokenizer.encode(messages, return_tensors='pt')
        # Move the encoded input to the same device as the model
        input_ids = input_ids.to(self.device)
        # Generate a response, adjusting parameters as needed
        output = self.model.generate(input_ids,  max_new_tokens=50, num_return_sequences=1)
        # Decode the generated response
        decoded_output = self.tokenizer.decode(output[0], skip_special_tokens=True)

        
  
        output = decoded_output[len(messages):]

        print(f"message: {message}")
        print(f"history: {history}")
        print(f"messages: {messages}")
        print(f"decoded_output: {decoded_output}")
        print(f"output: {output}")
        print(f"---------------------------------")
        
        yield output

        

        # # Function to count the number of tokens in the messages
        # def count_tokens(messages):
        #     result = sum(len(self.tokenizer.encode(messages, return_tensors='pt')))
        #     print(f"Tokens_in_context = {result}")
        #     return result

        # # Trim oldest messages if context length in tokens is exceeded
        # if count_tokens(messages) > self.context_length:
        #     # Remove the oldest message (after the system prompt)
        #     messages.pop(1)






