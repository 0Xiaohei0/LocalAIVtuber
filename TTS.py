import io
import os
from queue import Queue
import shutil
import threading
import zipfile
import numpy as np

import requests
from tqdm import tqdm
from pluginInterface import TTSPluginInterface
import gradio as gr
from pluginSelectionBase import PluginSelectionBase
import utils
from pydub import AudioSegment
import simpleaudio as sa
import pyaudio
from pydub import AudioSegment
from pydub.utils import audioop


class TTS(PluginSelectionBase):
    output_event_listeners = []

    input_queue = Queue()
    audio_data_queue = Queue()
    audio_process_thread = None
    audio_playback_thread = None

    def __init__(self) -> None:
        super().__init__(TTSPluginInterface)
        self.check_ffmpeg()

    def create_ui(self):
        with gr.Tab("TTS"):
            super().create_plugin_selection_ui()
            self.main_interface = gr.Interface(
                fn=self.wrapper_synthesize,
                inputs=[gr.Textbox(label="Original Text")],
                outputs=[gr.Audio(label="Synthesized Voice")],
                allow_flagging="never",
                examples=["すぅ…はぁ——おはようさん、朝の空気は清々しくて気持ちええなぁ、深呼吸して頭もすっきりや。",
                          "金魚飼ったことある？大人しゅうて、めっちゃ可愛ええんや。",
                          "全身ポカポカで気持ちええわぁ～、浮いとるみたい。",
                          "Ah... *yawns* Good morning. The morning air is the freshest. Come on, take a few extra breaths — it'll make you smarter~",
                          "Have you ever kept goldfish as pets? They're very cute.",
                          "Ah, this is great! I feel so relaxed all over, I could almost float away."]
            )
            gr.Markdown(
                "Note: Some prividers may only support certain languages.")
            super().create_plugin_ui()

    def wrapper_synthesize(self, text):
        result = self.current_plugin.synthesize(text)
        self.play_sound_from_bytes(result)
        return result

    VOICE_OUTPUT_FILENAME = "synthesized_voice.wav"

    def receive_input(self, text):
        self.input_queue.put(text)
        self.process_input_queue(self.current_plugin.synthesize)

    def process_input_queue(self, function):
        def generate_audio():
            while (not self.input_queue.empty()):
                # generate audio data and queue up for playing
                self.audio_data_queue.put(function(self.input_queue.get()))
                self.process_audio_queue(self.play_sound_from_bytes)

        # Check if the current thread is alive
        if self.audio_process_thread is None or not self.audio_process_thread.is_alive():
            # Create and start a new thread
            self.audio_process_thread = threading.Thread(target=generate_audio)
            self.audio_process_thread.start()

    def process_audio_queue(self, function):
        def play_audio():
            while (not self.audio_data_queue.empty()):
                # generate audio data and queue up for playing
                function(self.audio_data_queue.get())

        # Check if the current thread is alive
        if self.audio_playback_thread is None or not self.audio_playback_thread.is_alive():
            # Create and start a new thread
            self.audio_playback_thread = threading.Thread(target=play_audio)
            self.audio_playback_thread.start()

    def play_sound_from_bytes(self, audio_data, chunk_size=1024):
        """
        Play audio from bytes, analyze, and normalize volume in real time without breaks.
        Normalized volume will be in the range [0, 1].
        """
        # Open the audio data with PyDub
        audio = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")

        # Determine the maximum possible RMS value to scale normalization
        max_rms = self.find_max_rms(audio)

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(audio.sample_width),
                        channels=audio.channels,
                        rate=audio.frame_rate,
                        output=True,
                        frames_per_buffer=chunk_size)

        # Process and play audio in chunks
        for i in range(0, len(audio.raw_data), chunk_size):
            chunk_data = audio.raw_data[i:i+chunk_size]

            # Calculate RMS of this chunk and normalize to 0-1 scale
            rms = audioop.rms(chunk_data, audio.sample_width)
            normalized_volume = rms / max_rms
            print(f"Normalized Volume: {normalized_volume}")
            self.send_output(normalized_volume)
            # Play chunk
            stream.write(chunk_data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Close PyAudio
        p.terminate()

    def find_max_rms(self, audio_segment):
        """
        Find the maximum RMS value in the given audio segment.
        """
        chunk_size = 1024  # You can adjust the chunk size if needed
        max_rms = 0
        for i in range(0, len(audio_segment.raw_data), chunk_size):
            chunk_data = audio_segment.raw_data[i:i+chunk_size]
            rms = audioop.rms(chunk_data, audio_segment.sample_width)
            if rms > max_rms:
                max_rms = rms
        return max_rms

    def check_ffmpeg(self):
        # https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z

        # Check if the VoicevoxEngine folder exists
        if not os.path.exists("ffmpeg.exe"):
            # Define the file name and path for the ZIP file
            file_name = "ffmpeg-release-essentials.zip"

            # URL to download the ZIP file
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

            # Download the ZIP file with progress
            print(f"Downloading {file_name} from {url}...")
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                total_size_in_bytes = int(
                    response.headers.get('content-length', 0))
                block_size = 1024  # 1 Kibibyte

                progress_bar = tqdm(total=total_size_in_bytes,
                                    unit='iB', unit_scale=True)
                with open(file_name, 'wb') as file:
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
                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall()
                print(f"{file_name} extracted successfully.")

                current_module_directory = os.path.dirname(__file__)
                # Path to the ffmpeg.exe inside the extracted folder
                ffmpeg_exe_path = os.path.join(
                    'ffmpeg-6.1.1-essentials_build', 'bin', 'ffmpeg.exe')
                ffprobe_exe_path = os.path.join(
                    'ffmpeg-6.1.1-essentials_build', 'bin', 'ffprobe.exe')

                # Move ffmpeg.exe to the base directory
                shutil.move(ffmpeg_exe_path, current_module_directory)
                shutil.move(ffprobe_exe_path, current_module_directory)

                # Delete the extracted folder
                shutil.rmtree('ffmpeg-6.1.1-essentials_build')

                # Delete the ZIP file after extraction
                os.remove(file_name)

    def send_output(self, output):
        # print(output)
        for subcriber in self.output_event_listeners:
            subcriber(output)

    def add_output_event_listener(self, function):
        self.output_event_listeners.append(function)
