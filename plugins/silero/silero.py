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

    def init(self):

        print("initializing silero...")
        self.start_silero_server()
        # self.initialize_speakers()

    def synthesize(self, text):
        VoiceTextResponse = requests.request(
            "POST", f"http://{self.VOICE_VOX_URL_LOCAL}:50021/audio_query?text={text}&speaker={self.selected_style['id']}")
        AudioResponse = requests.request(
            "POST", f"http://{self.VOICE_VOX_URL_LOCAL}:50021/synthesis?speaker={self.selected_style['id']}", data=VoiceTextResponse)

        with open(self.VOICE_OUTPUT_FILENAME, "wb") as file:
            file.write(AudioResponse.content)
        return AudioResponse.content

    def create_ui(self):
        pass
        # self.speaker_names = self.get_speaker_names()
        # self.current_speaker = self.speaker_names[18]

        # self.current_styles = self.get_speaker_styles(self.current_speaker)
        # self.selected_style = self.current_styles[0]

        # with gr.Accordion(label="Plugin Options"):
        #     with gr.Row():
        #         self.speaker_dropdown = gr.Dropdown(
        #             choices=self.speaker_names,
        #             value=self.current_speaker,
        #             label="Speaker: "
        #         )
        #         self.style_dropdown = gr.Dropdown(
        #             choices=list(
        #                 map(lambda style: style['name'], self.current_styles)),
        #             value=self.selected_style['name'],
        #             label="Style: "
        #         )

        #         self.speaker_dropdown.input(self.on_speaker_change, inputs=[
        #                                     self.speaker_dropdown], outputs=[self.style_dropdown])
        #         self.style_dropdown.input(
        #             self.on_style_change, inputs=[self.style_dropdown])

        #     gr.Markdown(
        #         "You can also test out the voices here: https://voicevox.hiroshiba.jp/")

    def start_silero_server(self):
        if (self.silero_server_started):
            return

        # start silero server
        command = "python -m silero_api_server"
        subprocess.Popen(command, shell=True)
        self.silero_server_started = True

    def initialize_speakers(self):
        url = f"http://{self.VOICE_VOX_URL_LOCAL}:50021/speakers"
        while True:
            try:
                response = requests.request("GET", url)
                break
            except:
                print("Waiting for voicevox to start... ")
                time.sleep(0.5)
        self.speakersResponse = response.json()

    def get_speaker_names(self):
        speakerNames = list(
            map(lambda speaker: speaker['name'],  self.speakersResponse))
        return speakerNames

    def get_speaker_styles(self, speaker_name):
        speaker_styles = next(
            speaker['styles'] for speaker in self.speakersResponse if speaker['name'] == speaker_name)
        return speaker_styles

    def on_speaker_change(self, choice):
        # update styles dropdown
        self.current_styles = self.get_speaker_styles(choice)
        self.selected_style = self.current_styles[0]
        print(f"Changed speaker ID to: {self.selected_style['id']}")
        return gr.update(choices=list(
            map(lambda style: style['name'], self.current_styles)), value=self.selected_style['name'])

    def on_style_change(self, choice):
        self.selected_style = next(
            style for style in self.current_styles if choice == style['name'])
        print(f"Changed speaker ID to: {self.selected_style['id']}")
