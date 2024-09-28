

import json
import os
import re
import sys
from pluginInterface import TTSPluginInterface
import gradio as gr

sys.path.append(os.path.join(os.path.dirname(__file__), "GPT_SoVITS"))
sys.path.append(os.path.join(os.path.dirname(__file__)))
import GPT_SoVITS.api_direct as api


class GPT_SOVITS(TTSPluginInterface):

    current_module_directory = os.path.dirname(__file__)
    models_directory = os.path.join(
        current_module_directory, "models")
    OUTPUT_FILENAME = os.path.join(
        current_module_directory, "output.wav")
    CONFIG_FILENAME = os.path.join(
        current_module_directory, "config.json")
    
    voice_configs = []
    current_voice_config = None
    language = "en"

    def load_voice_config(self):
        with open(self.CONFIG_FILENAME, 'r', encoding='utf-8') as file:
            self.voice_configs = json.load(file)
            print(f"self.voice_configs {self.voice_configs}")
        if (not self.current_voice_config and len(self.voice_configs) > 0):
            self.current_voice_config = self.voice_configs[0]
            print(f"self.current_voice_config {self.current_voice_config}")

        print(self.current_voice_config)
        sovits_path = os.path.join(self.models_directory, self.current_voice_config["sovits_path"])
        gpt_path = os.path.join(self.models_directory, self.current_voice_config["gpt_path"])
        reference_audio_path = os.path.join(self.models_directory, self.current_voice_config["reference_audio_path"])
        reference_audio_text = self.current_voice_config["reference_audio_text"]
        reference_audio_language = self.current_voice_config["reference_audio_language"]
        
        # api.handle_change(reference_audio_path, reference_audio_text, reference_audio_language)
        # api.change_sovits_weights(sovits_path)
        # api.change_gpt_weights(gpt_path)
        api.init(sovits_path, gpt_path, reference_audio_path, reference_audio_text, reference_audio_language)

    def init(self):
        self.load_voice_config()
        

    def synthesize(self, text):
        text = self.preprocess_text(text)
        
        try:
            response = api.tts_endpoint(text=text, text_language=self.language)
            with open(self.OUTPUT_FILENAME, 'wb') as file:
                file.write(response)
        except Exception as e:
            print("Failed to generate audio file.", e)

        return response

    def create_ui(self):
        with gr.Accordion(label="Gpt-sovits Options", open=False):
            with gr.Row():
                self.voices_dropdown = gr.Dropdown(label="Voices:",
                                                   choices=self.get_voice_names(), value=self.current_voice_config['name'] if len(self.voice_configs) > 0 else None, interactive=True)
                self.voices_dropdown.change(self.change_voice, [self.voices_dropdown], [])
                self.refresh_button = gr.Button("Refresh", variant="primary")
                self.refresh_button.click(fn=self.refresh_choices, inputs=[], outputs=[self.voices_dropdown])
                self.language_dropdown = gr.Dropdown(label="languages:",
                                                   choices=["auto", "en", "zh", "ja"], value=self.language, interactive=True)
                self.language_dropdown.change(self.change_language, [self.language_dropdown], [])

    def change_voice(self, voice_name):
        for voice in self.voice_configs:
            if voice['name'] == voice_name:
                print(f"self.current_voice_config {self.current_voice_config}")
                self.current_voice_config = voice
                self.load_voice_config()
                return voice_name
        print(f"{voice_name} not found")
        print(f"self.voice_configs: {self.voice_configs}")

    def change_language(self,language):
        self.language = language

    def get_voice_names(self):
        return list(map(lambda x:x["name"], self.voice_configs))

    def refresh_choices(self):
        self.load_voice_config()
        voice_names = self.get_voice_names()
        return {"choices": voice_names, "__type__": "update"}
    
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