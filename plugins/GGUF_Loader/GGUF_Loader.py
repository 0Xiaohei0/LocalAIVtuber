import json
import requests
from tqdm import tqdm
from pluginInterface import LLMPluginInterface
import gradio as gr
from llama_cpp import Llama
import os


class GGUFLoader(LLMPluginInterface):
    context_length = 32768
    temperature = 0.9
    offload_gpu_layers = 0
    def init(self):
        # Directory where the module is located
        self.current_module_directory = os.path.dirname(__file__)

        self.default_model_filename = "aya-v0.2-q4_k_m.gguf"
        self.default_url = "https://huggingface.co/xiaoheiqaq/Aya-v0.2-Q4_K_M-GGUF/resolve/main/aya-v0.2-q4_k_m.gguf?download=true"
        
        self.model_data_path = os.path.join(self.current_module_directory, "model_data.json")

        # Initialize model filename and URL with defaults
        self.model_filename = self.default_model_filename
        url = self.default_url

        self.llm = None

        # Read model data from JSON file
        if os.path.exists(self.model_data_path):
            with open(self.model_data_path, 'r') as f:
                model_data = json.load(f)
                if model_data:
                    self.model_filename = model_data[0].get("fileName", self.default_model_filename)
                    url = model_data[0].get("link", self.default_url)

        self.model_directory = os.path.join(self.current_module_directory, "models")
        self.model_path = os.path.join(self.model_directory, self.model_filename)

        # Check if the model file exists
        if not os.path.exists(self.model_path):
            self.download_model(self.model_filename, url)

        # Initialize the model
        self.update_model(self.model_filename)

    def download_model(self, model_filename, url):
        if not os.path.exists(self.model_directory):
            os.makedirs(self.model_directory)

        model_path = os.path.join(self.model_directory, model_filename)
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
                self.update_model(model_filename)
        else:
            print(f"Failed to download the model. Status code: {response.status_code}")

    def create_ui(self):
        with gr.Accordion("GGUF Loader settings", open=False):
            with gr.Row():
                self.temperature_slider = gr.Slider(minimum=0, maximum=1, value=self.temperature, label="temperature")
                self.temperature_slider.change(fn=self.update_temperature, inputs=self.temperature_slider)
                self.gpu_offload_slider = gr.Slider(minimum=-1, maximum=100, step=1, value=self.offload_gpu_layers, label="offload gpu layers (-1 for all)")
                self.gpu_offload_slider.change(fn=self.update_gpu_offload, inputs=self.gpu_offload_slider)
            
            with gr.Row():
                model_data_path = os.path.join(os.path.dirname(__file__), "model_data.json")
                model_options = []
                if os.path.exists(model_data_path):
                    with open(model_data_path, 'r') as f:
                        model_data = json.load(f)
                        model_options = [model["fileName"] for model in model_data]

                self.model_dropdown = gr.Dropdown(choices=model_options, value=self.model_filename, label="Model")
                self.model_dropdown.change(fn=self.update_model, inputs=self.model_dropdown)
                self.download_button = gr.Button("Download")
                self.download_button.click(fn=self.download_selected_model, inputs=self.model_dropdown)

    def update_model(self, model_filename):
        current_module_directory = os.path.dirname(__file__)
        model_directory = os.path.join(current_module_directory, "models")
        self.model_path = os.path.join(model_directory, model_filename)

        if not os.path.exists(self.model_path):
            gr.Info(f"Model {model_filename} not found. Please press download to download the model.")
            return
        else:
            if self.llm:
                del self.llm
            self.llm = Llama(model_path=self.model_path, n_ctx=self.context_length, n_gpu_layers=self.offload_gpu_layers, seed=-1)
            gr.Info(f"Model changed to {model_filename}.")
            

    def download_selected_model(self, model_filename):
        gr.Info("downloading model... see progress in console")
        url = self.default_url
        if os.path.exists(self.model_data_path):
            with open(self.model_data_path, 'r') as f:
                model_data = json.load(f)
                for model in model_data:
                    if model["fileName"] == model_filename:
                        url = model.get("link", self.default_url)
                        break

        self.download_model(model_filename, url)

    def update_temperature(self, t):
        self.temperature = t

    def update_gpu_offload(self, val):
        self.offload_gpu_layers = val

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
        print(f"Generating with temperature {self.temperature}")

        completion_chunks = self.llm.create_chat_completion(
            messages, stream=True, temperature=self.temperature)
        output = ""
        for completion_chunk in completion_chunks:
            try:
                text = completion_chunk['choices'][0]['delta']['content']
                output += text
                yield output
            except:
                pass
