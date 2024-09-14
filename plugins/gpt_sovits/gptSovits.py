

import os
import re
import sys
from pluginInterface import TTSPluginInterface
import gradio as gr

sys.path.append(os.path.join(os.path.dirname(__file__), "GPT_SoVITS"))
sys.path.append(os.path.join(os.path.dirname(__file__)))
import GPT_SoVITS.api_direct as api

class GPTSOVITS_Plugin(TTSPluginInterface):

    current_module_directory = os.path.dirname(__file__)
    OUTPUT_FILENAME = os.path.join(
        current_module_directory, "output.wav")
   

    def init(self):
        api.init()

    def synthesize(self, text):
        text = self.preprocess_text(text)
        response = api.tts_endpoint(text=text, text_language='auto')

        try:
            with open(self.OUTPUT_FILENAME, 'wb') as file:
                file.write(response)
        except Exception as e:
            print("Failed to generate audio file.", e)

        return response


       

    def create_ui(self):
        with gr.Accordion(label="Gpt-sovits Options", open=False):
            with gr.Row():
                # self.rvc_model_dropdown = gr.Dropdown(label="RVC models:",
                #                                         choices=self.rvc_model_names, value=self.rvc_model_name if len(self.rvc_model_names) > 0 else None, interactive=True)
                self.refresh_button = gr.Button("Refresh", variant="primary")

    def preprocess_text(self, text):
        print(f"replacing decimal point with the word point.")
        print(f"original:) {text}")

        pattern = r'\b\d*\.\d+\b'

        def replace_match(match):
            decimal_number = match.group(0)
            return decimal_number.replace('.', ' point ')

        # Replace all occurrences of decimal patterns in the text
        replaced_text = re.sub(pattern, replace_match, text)
        print(f"replaced_text: {replaced_text}")
        
        return replaced_text