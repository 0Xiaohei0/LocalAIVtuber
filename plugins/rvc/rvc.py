import io
import numpy as np
from pydub import AudioSegment
import gradio as gr
import asyncio
from pluginInterface import TTSPluginInterface
import os
import edge_tts


class RVC(TTSPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    VOICE_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "synthesized_voice.mp3")

    def init(self):
        pass

    def synthesize(self, text):

        print(f'Outputting audio to {self.VOICE_OUTPUT_FILENAME}')
        # print(f'{string}')
        VOICE = "en-GB-SoniaNeural"
        communicate = edge_tts.Communicate(text, VOICE)
        asyncio.run(communicate.save(self.VOICE_OUTPUT_FILENAME))

        # Load the MP3 file
        audio = AudioSegment.from_mp3(self.VOICE_OUTPUT_FILENAME)

        # Convert it to WAV format
        wav_filename = self.VOICE_OUTPUT_FILENAME.replace('.mp3', '.wav')
        audio.export(wav_filename, format='wav')
        audio = AudioSegment.from_wav(wav_filename)
        samples = np.array(audio.get_array_of_samples())

        # Gradio expects (sample_rate, audio_array)
        return (audio.frame_rate, samples)

    def create_ui(self):
        with gr.Accordion(label="rvc Options", open=False):
            gr.Markdown(
                "test")
