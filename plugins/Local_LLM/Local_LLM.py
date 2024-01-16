from pluginInterface import LLMPluginInterface
import gradio as gr
from llama_cpp import Llama
import os


class LocalLLM(LLMPluginInterface):
    def init(self):
        current_module_directory = os.path.dirname(__file__)
        model_path = os.path.join(
            current_module_directory, "models", "dolphin-2.2.1-mistral-7b.Q4_K_M.gguf")
        self.llm = Llama(model_path=model_path,
                         chat_format="chatml", n_ctx=2048)

    def predict(self, message, history, system_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        for entry in history:
            user, ai = entry
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": ai})

        messages.append({"role": "user", "content": message})

        # print(f"message: {message}")
        # print(f"history: {history}")
        # print(f"messages: {messages}")
        # print(f"---------------------------------")

        completion_chunks = self.llm.create_chat_completion(
            messages, stream=True)
        output = ""
        for completion_chunk in completion_chunks:
            try:
                text = completion_chunk['choices'][0]['delta']['content']
                output += text
                yield output
            except:
                pass
