import subprocess
import time
import zipfile
import gradio as gr
import requests
from tqdm import tqdm
from pluginInterface import TTSPluginInterface
import os


class Silero(TTSPluginInterface):
    silero_server_started = False
    SILERO_URL_LOCAL = "127.0.0.1"

    def init(self):
        print("initializing silero...")
        self.start_silero_server()

    def synthesize(self, text):
        VoiceTextResponse = requests.request(
            "POST", f"http://{self.VOICE_VOX_URL_LOCAL}:50021/audio_query?text={text}&speaker={self.selected_style['id']}")
        AudioResponse = requests.request(
            "POST", f"http://{self.VOICE_VOX_URL_LOCAL}:50021/synthesis?speaker={self.selected_style['id']}", data=VoiceTextResponse)

        with open(self.VOICE_OUTPUT_FILENAME, "wb") as file:
            file.write(AudioResponse.content)
        return AudioResponse.content

    def create_ui(self):
        language_names = self.get_langauges()
        speaker_names = self.get_speaker_names()
        with gr.Accordion(label="Silero Options"):
            with gr.Row():
                self.language_dropdown = gr.Dropdown(
                    choices=language_names,
                    value="v3_en.pt",
                    label="Language: "
                )
                self.speaker_dropdown = gr.Dropdown(
                    choices=speaker_names,
                    value=speaker_names[0],
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
        command = "python -m silero_api_server"
        subprocess.Popen(command, shell=True)
        self.silero_server_started = True

    def get_langauges(self):
        url = f"http://{self.SILERO_URL_LOCAL}:8001/tts/language"
        while True:
            try:
                response = requests.request("GET", url)
                break
            except:
                print("Waiting for silero to start... ")
                time.sleep(0.5)
        return response.json()

    def get_speakers(self):
        url = f"http://{self.SILERO_URL_LOCAL}:8001/tts/speakers"
        while True:
            try:
                response = requests.request("GET", url)
                break
            except:
                print("Waiting for silero to start... ")
                time.sleep(0.5)
        return response.json()

    def get_speaker_names(self):
        return [speaker['name'] for speaker in self.get_speakers()]

    def on_language_change(self, choice):
        # update speakers dropdown
        url = f"http://{self.SILERO_URL_LOCAL}:8001/tts/language"
        data = {
            "id": choice
        }
        requests.request("POST", url, json=data)
        print(f"Changed language to: {choice}")
        speaker_names = self.get_speaker_names()
        return gr.update(choices=speaker_names, value=speaker_names[0])

    def on_speaker_change(self, choice):

        print(f"Changed speaker to: {choice}")
