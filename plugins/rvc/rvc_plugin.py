from .inferrvc import load_torchaudio
from .inferrvc import RVC
import edge_tts
import os
from pluginInterface import TTSPluginInterface
import asyncio
import gradio as gr
from pydub import AudioSegment
import numpy as np
import soundfile as sf
from .edge_tts_voices import SUPPORTED_VOICES


class RVCPlugin(TTSPluginInterface):

    current_module_directory = os.path.dirname(__file__)
    EDGE_TTS_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "edgetts_output.mp3")
    RVC_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "rvc_output.wav")
    rvc_model_dir = os.path.join(current_module_directory, "rvc_model_dir")
    rvc_index_dir = os.path.join(current_module_directory, "rvc_index_dir")

    edge_tts_voice = "en-US-AnaNeural"
    rvc_model_name = 'kikuri.pth'

    def init(self):
        # where model.pth files are stored.
        os.environ['RVC_MODELDIR'] = self.rvc_model_dir
        # where model.index files are stored.
        os.environ['RVC_INDEXDIR'] = self.rvc_index_dir
        # the audio output frequency, default is 44100.
        os.environ['RVC_OUTPUTFREQ'] = '44100'
        # If the output audio tensor should block until fully loaded, this can be ignored. But if you want to run in a larger torch pipeline, setting to False will improve performance a little.
        os.environ['RVC_RETURNBLOCKING'] = 'True'

        self.model = RVC(self.rvc_model_name)
        print(self.model.name)
        print('Paths', self.model.model_path, self.model.index_path)
        self.update_rvc_model_list()

    def synthesize(self, text):

        print(f'Outputting audio to {self.EDGE_TTS_OUTPUT_FILENAME}')
        communicate = edge_tts.Communicate(text, self.edge_tts_voice)
        asyncio.run(communicate.save(self.EDGE_TTS_OUTPUT_FILENAME))

        # Load the MP3 file
        audio = AudioSegment.from_mp3(self.EDGE_TTS_OUTPUT_FILENAME)

        # Convert it to WAV format
        wav_filename = self.EDGE_TTS_OUTPUT_FILENAME.replace('.mp3', '.wav')
        audio.export(wav_filename, format='wav')
        audio = AudioSegment.from_wav(wav_filename)
        samples = np.array(audio.get_array_of_samples())

        aud, sr = load_torchaudio(wav_filename)
        paudio1 = self.model(aud, f0_up_key=0, output_device='cpu',
                             output_volume=RVC.MATCH_ORIGINAL, index_rate=.75)

        sf.write(self.RVC_OUTPUT_FILENAME, paudio1, 44100)

        audio = AudioSegment.from_wav(self.RVC_OUTPUT_FILENAME)
        samples = np.array(audio.get_array_of_samples())

        # Gradio expects (sample_rate, audio_array)
        return (audio.frame_rate, samples)

    def create_ui(self):
        with gr.Accordion(label="rvc Options", open=False):
            with gr.Row():
                self.edge_tts_speaker_dropdown = gr.Dropdown(
                    choices=SUPPORTED_VOICES,
                    value=self.edge_tts_voice,
                    label="edge_tts_speaker: "
                )
                self.rvc_model_dropdown = gr.Dropdown(label="RVC models:",
                                                      choices=self.rvc_model_names, value=self.rvc_model_names[0] if len(self.rvc_model_names) > 0 else None, interactive=True)
                self.refresh_button = gr.Button("Refresh", variant="primary")

                self.rvc_model_dropdown.input(self.on_rvc_model_change, inputs=[
                    self.rvc_model_dropdown], outputs=[])
                self.refresh_button.click(
                    self.on_refresh, outputs=[self.rvc_model_dropdown])

                self.edge_tts_speaker_dropdown.input(self.on_speaker_change, inputs=[
                    self.edge_tts_speaker_dropdown], outputs=[])
                # self.style_dropdown.input(
                #     self.on_style_change, inputs=[self.style_dropdown])
            gr.Markdown(
                "test")

    def on_speaker_change(self, choice):
        self.edge_tts_voice = choice

    def on_rvc_model_change(self, choice):
        self.rvc_model_name = choice
        self.model = RVC(self.rvc_model_name)

    def on_refresh(self):
        self.update_rvc_model_list()
        return gr.update(choices=self.rvc_model_names)

    def update_rvc_model_list(self):
        self.rvc_model_names = []
        for name in os.listdir(self.rvc_model_dir):
            if name.endswith(".pth"):
                self.rvc_model_names.append(name)
                print(self.rvc_model_names)
