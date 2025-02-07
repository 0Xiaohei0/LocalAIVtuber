
import os
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
from .languages import LANGUAGES

class VoiceInputLive(InputPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    MIC_OUTPUT_PATH = os.path.join(
        current_module_directory, "voice_recording.wav")

    key_to_bind = "ctrl+a"  # Default binding

    def init(self):
        self.liveTextbox = LiveTextbox()

    def create_ui(self):
        with gr.Accordion("Voice Input",open=False):
            with gr.Row():
                self.start_listening_button = gr.Button(
                    "start Listening", self.start_listening)
                self.stop_listening_button = gr.Button(
                    "stop Listening", self.stop_listening)
            with gr.Row():
                language_list = list(LANGUAGES.values())
                language_list.insert(0, 'auto')
                self.language_dropdown = gr.Dropdown(language_list, value=self.input_language, label="Input languages")
            with gr.Accordion("Console"):
                self.liveTextbox.create_ui()

        self.start_listening_button.click(self.start_listening)
        self.stop_listening_button.click(self.stop_listening)
        self.language_dropdown.input(self.on_language_change, inputs=[self.language_dropdown])

    def on_language_change(self, choice):
        self.input_language = choice
        self.liveTextbox.print(f"changed language to {choice}")
    

    def start_listening(self):
        gr.Info("starting listening...")
        self.recording = True
        thread = Thread(target=self.transcribe_loop)
        thread.start()
        self.liveTextbox.print("Started listening...")

    def stop_listening(self):
        gr.Info("Stopping listening...")
        self.recording = False
        self.ambience_adjusted = False
        self.liveTextbox.print("Stopped listening...")
        

    def transcribe_loop(self):
        while self.recording:
            self.transcribe()
    def transcribe(self):
        pass
