import requests
from tqdm import tqdm
from pluginInterface import LLMPluginInterface
import gradio as gr
from llama_cpp import Llama
import os


class LocalLLM(LLMPluginInterface):
    context_length = 4096

    def init(self):
        # Directory where the module is located
        current_module_directory = os.path.dirname(__file__)
        model_filename = "dolphin-2.2.1-mistral-7b.Q4_K_M.gguf"
        model_directory = os.path.join(current_module_directory, "models")
        model_path = os.path.join(model_directory, model_filename)

        # Check if the model file exists
        if not os.path.exists(model_path):
            # If not, create the models directory if it does not exist
            if not os.path.exists(model_directory):
                os.makedirs(model_directory)

            # URL to download the model
            url = "https://huggingface.co/TheBloke/dolphin-2.2.1-mistral-7B-GGUF/resolve/main/dolphin-2.2.1-mistral-7b.Q4_K_M.gguf?download=true"
            
             # Download the file with progress
            print(f"Downloading model from {url}...")
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                total_size_in_bytes = int(response.headers.get('content-length', 0))
                block_size = 1024  # 1 Kibibyte

                progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
                with open(model_path, 'wb') as file:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file.write(data)
                progress_bar.close()

                if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                    print("ERROR, something went wrong during download")
                else:
                    print("Model downloaded successfully.")
            else:
                print(f"Failed to download the model. Status code: {response.status_code}")
                return

        # Initialize the model
        self.llm = Llama(model_path=model_path,
                         chat_format="chatml", n_ctx=self.context_length, n_gpu_layers=-1)


# https://huggingface.co/TheBloke/dolphin-2.2.1-mistral-7B-GGUF/blob/main/dolphin-2.2.1-mistral-7b.Q4_K_M.gguf
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
