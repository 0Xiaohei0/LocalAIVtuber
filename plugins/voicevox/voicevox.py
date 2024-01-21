import subprocess
import time
import zipfile
import gradio as gr
import requests
from tqdm import tqdm
from pluginInterface import TTSPluginInterface
import os


class VoiceVox(TTSPluginInterface):
    voicevox_server_started = False
    current_module_directory = os.path.dirname(__file__)
    voicevox_engine_directory = os.path.join(
        current_module_directory, "VOICEVOX")
    executable_path = os.path.join(voicevox_engine_directory, "run.exe")
    VOICE_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "synthesized_voice.wav")
    VOICE_VOX_URL_LOCAL = "127.0.0.1"

    def init(self):
        # Define the directory and file name
        file_name = "voicevox-windows-directml-0.14.11.zip"
        file_path = os.path.join(self.current_module_directory, file_name)

        # Check if the VoicevoxEngine folder exists
        if not os.path.exists(self.voicevox_engine_directory):
            # Define the file name and path for the ZIP file
            file_name = "voicevox-windows-directml-0.14.11.zip"
            file_path = os.path.join(self.current_module_directory, file_name)

            # URL to download the ZIP file
            url = "https://github.com/VOICEVOX/voicevox/releases/download/0.14.11/voicevox-windows-directml-0.14.11.zip"

            # Download the ZIP file with progress
            print(f"Downloading {file_name} from {url}...")
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                total_size_in_bytes = int(
                    response.headers.get('content-length', 0))
                block_size = 1024  # 1 Kibibyte

                progress_bar = tqdm(total=total_size_in_bytes,
                                    unit='iB', unit_scale=True)
                with open(file_path, 'wb') as file:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file.write(data)
                progress_bar.close()

                if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                    print("ERROR, something went wrong during download")
                else:
                    print(f"{file_name} downloaded successfully.")

                # Extract and rename the ZIP file contents
                print(f"Extracting {file_name}...")
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.current_module_directory)
                print(f"{file_name} extracted to VoicevoxEngine successfully.")

                # Optionally, delete the ZIP file after extraction
                os.remove(file_path)
            else:
                print(
                    f"Failed to download {file_name}. Status code: {response.status_code}")
                return

        print("initializing voicevox...")
        self.start_voicevox_server()
        self.initialize_speakers()

    def synthesize(self, text):
        VoiceTextResponse = requests.request(
            "POST", f"http://{self.VOICE_VOX_URL_LOCAL}:50021/audio_query?text={text}&speaker={self.selected_style['id']}")
        AudioResponse = requests.request(
            "POST", f"http://{self.VOICE_VOX_URL_LOCAL}:50021/synthesis?speaker={self.selected_style['id']}", data=VoiceTextResponse)

        with open(self.VOICE_OUTPUT_FILENAME, "wb") as file:
            file.write(AudioResponse.content)
        return AudioResponse.content

    def create_ui(self):
        self.speaker_names = self.get_speaker_names()
        self.current_speaker = self.speaker_names[18]

        self.current_styles = self.get_speaker_styles(self.current_speaker)
        self.selected_style = self.current_styles[0]

        with gr.Accordion(label="Voicevox Options", open=False):
            with gr.Row():
                self.speaker_dropdown = gr.Dropdown(
                    choices=self.speaker_names,
                    value=self.current_speaker,
                    label="Speaker: "
                )
                self.style_dropdown = gr.Dropdown(
                    choices=list(
                        map(lambda style: style['name'], self.current_styles)),
                    value=self.selected_style['name'],
                    label="Style: "
                )

                self.speaker_dropdown.input(self.on_speaker_change, inputs=[
                                            self.speaker_dropdown], outputs=[self.style_dropdown])
                self.style_dropdown.input(
                    self.on_style_change, inputs=[self.style_dropdown])

            gr.Markdown(
                "You can also test out the voices here: https://voicevox.hiroshiba.jp/")

    def start_voicevox_server(self):
        if (self.voicevox_server_started):
            return
        # start voicevox server
        subprocess.Popen(self.executable_path)
        self.voicevox_server_started = True

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
