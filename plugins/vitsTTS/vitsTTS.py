
import gradio as gr
from pluginInterface import TTSPluginInterface
import os
from .TTService import TTService
import pyaudio
import wave
import numpy as np

current_module_directory = os.path.dirname(__file__)
model_dir = os.path.join(current_module_directory, "models")
output_dir = os.path.join(current_module_directory, "output.wav")
cfg = os.path.join(model_dir, "chisato.json")
model = os.path.join(model_dir, "chisato.pth")
    


class VitsTTS(TTSPluginInterface):

    def init(self):
        self.a = TTService(cfg, model, 'test', 1)
        self.p = pyaudio.PyAudio()


    def synthesize(self, text):
        audio = self.a.read(f'[JA]{text}[JA]')
        # audio = self.a.read('[ZH]今天天气真好！[ZH]')
        stream = self.p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=self.a.hps.data.sampling_rate,
                        output=True
                        )
        data = audio.astype(np.float32).tobytes()
        stream.write(data)
        # Set the output file name
        output_file = output_dir

        # Set the audio properties
        num_channels = 1
        sample_width = 2  # Assuming 16-bit audio
        frame_rate = self.a.hps.data.sampling_rate

        # Convert audio data to 16-bit integers
        audio_int16 = (audio * np.iinfo(np.int16).max).astype(np.int16)

        # Open the output file in write mode
        with wave.open(output_file, 'wb') as wav_file:
            # Set the audio properties
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(frame_rate)

            # Write audio data to the file
            wav_file.writeframes(audio_int16.tobytes())

    def create_ui(self):
        with gr.Accordion(label="Vits Options", open=False):
            with gr.Row():
                pass

    