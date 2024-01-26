from .inferrvc import load_torchaudio
from .inferrvc import RVC
import edge_tts
import os
from pluginInterface import TTSPluginInterface
import asyncio
import gradio as gr
from pydub import AudioSegment
import numpy as np
import io
import soundfile as sf


class RVCPlugin(TTSPluginInterface):

    current_module_directory = os.path.dirname(__file__)
    EDGE_TTS_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "edgetts_output.mp3")
    RVC_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "rvc_output.wav")
    rvc_model_dir = os.path.join(current_module_directory, "rvc_model_dir")
    rvc_index_dir = os.path.join(current_module_directory, "rvc_index_dir")

    def init(self):
        # where model.pth files are stored.
        os.environ['RVC_MODELDIR'] = self.rvc_model_dir
        # where model.index files are stored.
        os.environ['RVC_INDEXDIR'] = self.rvc_index_dir
        # the audio output frequency, default is 44100.
        os.environ['RVC_OUTPUTFREQ'] = '44100'
        # If the output audio tensor should block until fully loaded, this can be ignored. But if you want to run in a larger torch pipeline, setting to False will improve performance a little.
        os.environ['RVC_RETURNBLOCKING'] = 'True'

        self.kikuri = RVC(
            'kikuri.pth', index='added_IVF571_Flat_nprobe_1_kikuri_v2')
        print(self.kikuri.name)
        print('Paths', self.kikuri.model_path, self.kikuri.index_path)

    def synthesize(self, text):

        print(f'Outputting audio to {self.EDGE_TTS_OUTPUT_FILENAME}')
        # print(f'{string}')
        VOICE = "en-GB-SoniaNeural"
        communicate = edge_tts.Communicate(text, VOICE)
        asyncio.run(communicate.save(self.EDGE_TTS_OUTPUT_FILENAME))

        # Load the MP3 file
        audio = AudioSegment.from_mp3(self.EDGE_TTS_OUTPUT_FILENAME)

        # Convert it to WAV format
        wav_filename = self.EDGE_TTS_OUTPUT_FILENAME.replace('.mp3', '.wav')
        audio.export(wav_filename, format='wav')
        audio = AudioSegment.from_wav(wav_filename)
        samples = np.array(audio.get_array_of_samples())

        aud, sr = load_torchaudio(wav_filename)
        paudio1 = self.kikuri(aud, f0_up_key=6, output_device='cpu',
                              output_volume=RVC.MATCH_ORIGINAL, index_rate=.75)

        sf.write(self.RVC_OUTPUT_FILENAME, paudio1, 44100)

        audio = AudioSegment.from_wav(self.RVC_OUTPUT_FILENAME)
        samples = np.array(audio.get_array_of_samples())

        # Gradio expects (sample_rate, audio_array)
        return (audio.frame_rate, samples)

    def create_ui(self):
        with gr.Accordion(label="rvc Options", open=False):
            gr.Markdown(
                "test")
