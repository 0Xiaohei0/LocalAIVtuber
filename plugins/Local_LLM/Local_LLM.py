from pluginInterface import LLMPluginInterface
import gradio as gr
from llama_cpp import Llama
import os


class LocalLLM(LLMPluginInterface):
    context_length = 4096

    def init(self):
        current_module_directory = os.path.dirname(__file__)
        model_path = os.path.join(
            current_module_directory, "models", "mistral-7b-instruct-v0.1.Q4_K_M.gguf")
        self.llm = Llama(model_path=model_path,
                         chat_format="chatml", n_ctx=self.context_length)

    def predict(self, message, history, system_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        for entry in history:
            user, ai = entry
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": ai})

        messages.append({"role": "user", "content": message})

        # Function to count the number of tokens in the messages
        def count_tokens(msg_list):
            result = sum(len(self.llm.tokenize(
                str.encode(msg['content']))) for msg in msg_list)
            print(f"Tokens_in_context = {result}")
            return result

        # Trim oldest messages if context length in tokens is exceeded
        while count_tokens(messages) > self.context_length and len(messages) > 1:
            # Remove the oldest message (after the system prompt)
            messages.pop(1)

        print(f"message: {message}")
        print(f"history: {history}")
        print(f"messages: {messages}")
        print(f"---------------------------------")

        completion_chunks = self.llm.create_chat_completion(
            messages, stream=True, temperature=0.95)
        output = ""
        for completion_chunk in completion_chunks:
            try:
                text = completion_chunk['choices'][0]['delta']['content']
                output += text
                yield output
            except:
                pass
