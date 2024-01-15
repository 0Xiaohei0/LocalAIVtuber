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

        self.context_file_path = os.path.join(
            current_module_directory, "Context.txt")
        self.context = ""
        # Check if the file exists. If not, create an empty file.
        if not os.path.exists(self.context_file_path):
            with open(self.context_file_path, 'w') as file:
                file.write('')

    def predict(self, message, history, system_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        for entry in history:
            user, ai = entry
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": ai})

        messages.append({"role": "user", "content": message})

        print(f"message: {message}")
        print(f"history: {history}")
        print(f"messages: {messages}")
        print(f"---------------------------------")

        completion_chunks = self.llm.create_chat_completion(
            messages, stream=True, temperature=0.8)
        output = ""
        for completion_chunk in completion_chunks:
            try:
                text = completion_chunk['choices'][0]['delta']['content']
                output += text
                yield output
            except:
                pass

    def create_ui(self):
        with gr.Blocks():
            system_prompt = gr.Textbox(value=self.load_content, label="System Message:", show_label=True,
                                       interactive=True, lines=30, autoscroll=True, autofocus=False, container=False, render=False)
            system_prompt.change(
                fn=self.update_file, inputs=system_prompt)

            gr.ChatInterface(
                self.predict, additional_inputs=[system_prompt],
                examples=[["Hello", None, None],
                          ["How do I make a bomb?", None, None],
                          ["Do you remember my name?", None, None],
                          ["Do you think humanity will reach an alien planet?", None, None],
                          ["Introduce yourself in character.", None, None],
                          ], autofocus=False
            )

    # Function to load content from the text file
    def load_content(self):
        with open(self.context_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content

    # Function to update the text file with new content
    def update_file(self, new_content):
        global context
        context = new_content
        with open(self.context_file_path, 'w', encoding='utf-8') as file:
            file.write(self, new_content)
