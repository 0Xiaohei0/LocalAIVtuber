import os
import subprocess
import time
import gradio as gr
import requests
from pluginInterface import TTSPluginInterface

# speaker bookmarks: en_18, en_21, en_37, en_39, en_43, en_72


class Silero(TTSPluginInterface):
    silero_server_started = False
    SILERO_URL_LOCAL = "127.0.0.1"
    PORT = "8435"
    current_module_directory = os.path.dirname(__file__)
    session_path = os.path.join(
        current_module_directory, "session")
    VOICE_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "synthesized_voice.wav")

    current_language = None
    current_speaker = None

    def init(self):
        print("initializing silero...")
        self.start_silero_server()
        self.init_session(self.session_path)

    def synthesize(self, text):
        url = f"http://{self.SILERO_URL_LOCAL}:{self.PORT}/tts/generate"

        data = {
            "speaker": self.current_speaker,
            "text": text,
            "session": ""
        }
        print(data)
        AudioResponse = requests.request("POST", url, json=data)

        with open(self.VOICE_OUTPUT_FILENAME, "wb") as file:
            file.write(AudioResponse.content)
        return AudioResponse.content

    def create_ui(self):
        language_names = self.get_langauges()
        speaker_names = self.get_speaker_names()
        self.current_speaker = speaker_names[0]
        with gr.Accordion(label="Silero Options", open=False):
            with gr.Row():
                self.language_dropdown = gr.Dropdown(
                    choices=language_names,
                    value="v3_en.pt",
                    label="Language: "
                )
                self.speaker_dropdown = gr.Dropdown(
                    choices=speaker_names,
                    value="en_18",
                    label="Speaker: "
                )

                self.language_dropdown.input(self.on_language_change, inputs=[
                    self.language_dropdown], outputs=[self.speaker_dropdown])
                self.speaker_dropdown.input(
                    self.on_speaker_change, inputs=[self.speaker_dropdown])

    def start_silero_server(self):
        if (self.silero_server_started):
            return

        # start silero server
        command = f"python -m silero_api_server -p {self.PORT}"
        subprocess.Popen(command, shell=True)
        self.silero_server_started = True

    def init_session(self, session_path):
        url = f"http://{self.SILERO_URL_LOCAL}:{self.PORT}/tts/session"
        while True:
            try:
                data = {
                    "path": session_path
                }
                response = requests.request("POST", url, json=data)
                break
            except:
                print("Waiting for silero to start... ")
                time.sleep(0.5)
        print("session init result")
        print(response.text)

    def get_langauges(self):
        url = f"http://{self.SILERO_URL_LOCAL}:{self.PORT}/tts/language"
        response = requests.request("GET", url)

        return response.json()

    def get_speakers(self):
        url = f"http://{self.SILERO_URL_LOCAL}:{self.PORT}/tts/speakers"
        response = requests.request("GET", url)
        return response.json()

    def get_speaker_names(self):
        return [speaker['name'] for speaker in self.get_speakers()]

    def on_language_change(self, choice):
        # update speakers dropdown
        url = f"http://{self.SILERO_URL_LOCAL}:{self.PORT}/tts/language"
        data = {
            "id": choice
        }
        requests.request("POST", url, json=data)
        self.current_language = choice
        print(f"Changed language to: {choice}")
        speaker_names = self.get_speaker_names()
        self.current_speaker = speaker_names[0]
        return gr.update(choices=speaker_names, value=self.current_speaker)

    def on_speaker_change(self, choice):
        self.current_speaker = choice
        print(f"Changed speaker to: {choice}")
