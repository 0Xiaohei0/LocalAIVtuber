import sys
import requests
import os
import gradio as gr
from pluginInterface import TTSPluginInterface
import subprocess
current_module_directory = os.path.dirname(__file__)
sys.path.append(current_module_directory)
from gpt_sovits.GPT_SoVITS.api_direct import tts_endpoint


class gptSovits(TTSPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    output_dir = os.path.join(current_module_directory, "output.wav")
    server_dir = os.path.join(current_module_directory, "GPT_SoVITS")
    lang = ["zh","en","ja"]
    language = "en"
    url = "http://127.0.0.1:9880"

    def synthesize(self, text):
        response = tts_endpoint(text=text, text_language=self.language)

        try:
            with open(self.output_dir, 'wb') as file:
                file.write(response)
            print("Audio file downloaded successfully:", self.output_dir)
        except Exception as e:
            print("Failed to download audio file.", e)
            
        return response


    def create_ui(self):
        with gr.Accordion(label="gpt-sovits Options", open=False):
            with gr.Row():
                self.language_dropdown = gr.Dropdown(choices=self.lang, value=self.language, label='language')
                
        self.language_dropdown.change(self.update_language, inputs=[self.language_dropdown])
    
    def update_language(self, input):
        self.language = input
    
    
