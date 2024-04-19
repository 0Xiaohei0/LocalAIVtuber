
import io
import gradio as gr
from pluginInterface import TTSPluginInterface
import pyaudio
import wave
import numpy as np
from pydub import AudioSegment
import os
import torch
from torch import no_grad, LongTensor
import argparse

from .vits.commons import * 
from .vits.utils import *
from .vits.mel_processing import spectrogram_torch
from .vits.models import SynthesizerTrn
import gradio as gr
import librosa
import soundfile as sf

from .vits.text import text_to_sequence, _clean_text

current_module_directory = os.path.dirname(__file__)
model_dir = os.path.join(current_module_directory, "models")
output_dir = os.path.join(current_module_directory, "output.wav")
config_dir = os.path.join(model_dir, "xiangling.json")
model = os.path.join(model_dir, "xiangling.pth")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
language_marks = {
    "Japanese": "",
    "日本語": "[JA]",
    "简体中文": "[ZH]",
    "English": "[EN]",
    "Mix": "",
}
lang = ['日本語', '简体中文', 'English', 'Mix']


class VitsTTS(TTSPluginInterface):

    def init(self):
        hps = get_hparams_from_file(config_dir)
        net_g = SynthesizerTrn(
            len(hps.symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            **hps.model).to(device)
        _ = net_g.eval()

        _ = load_checkpoint(model, net_g, None)
        speaker_ids = hps.speakers
        self.speakers = list(hps.speakers.keys())
        self.tts_fn = self.create_tts_fn(net_g, hps, speaker_ids)

    def synthesize(self, text):
        text_output, (sampling_rate, audio) = self.tts_fn(text, self.char_dropdown.value,self.language_dropdown.value,self.duration_slider.value)
        sf.write(output_dir, audio, samplerate=sampling_rate, format='WAV')
    
        # Save the audio to a BytesIO stream as a WAV file to return bytes
        with io.BytesIO() as audio_buffer:
            sf.write(audio_buffer, audio, samplerate=sampling_rate, format='WAV')
            audio_buffer.seek(0)  # Go to the start of the buffer
            wav_bytes = audio_buffer.read()  # Read the WAV file bytes
            
        return wav_bytes


    def create_ui(self):
        with gr.Accordion(label="Vits Options", open=False):
            with gr.Row():
                with gr.Column():
                    self.textbox = gr.TextArea(label="Text",
                                          placeholder="Type your sentence here",
                                          value="Hello.", elem_id=f"tts-input")
                    # select character
                    self.char_dropdown = gr.Dropdown(choices=self.speakers, value=self.speakers[0], label='character')
                    self.language_dropdown = gr.Dropdown(choices=lang, value=lang[2], label='language')
                    self.duration_slider = gr.Slider(minimum=0.1, maximum=5, value=1, step=0.1,
                                                label='速度 Speed')
                with gr.Column():
                    self.text_output = gr.Textbox(label="Message")
                    self.audio_output = gr.Audio(label="Output Audio", elem_id="tts-audio")
                    btn = gr.Button("Generate!")
                    btn.click(self.tts_fn,
                              inputs=[self.textbox, self.char_dropdown, self.language_dropdown, self.duration_slider,],
                              outputs=[self.text_output, self.audio_output])
    

    def get_text(self, text, hps, is_symbol):
        text_norm = text_to_sequence(text, hps.symbols, [] if is_symbol else hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = intersperse(text_norm, 0)
        text_norm = LongTensor(text_norm)
        return text_norm

    def create_tts_fn(self, model, hps, speaker_ids):
        def tts_fn(text, speaker, language, speed):
            if language is not None:
                text = language_marks[language] + text + language_marks[language]
            speaker_id = speaker_ids[speaker]
            stn_tst = self.get_text(text, hps, False)
            with no_grad():
                x_tst = stn_tst.unsqueeze(0).to(device)
                x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
                sid = LongTensor([speaker_id]).to(device)
                audio = model.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8,
                                    length_scale=1.0 / speed)[0][0, 0].data.cpu().float().numpy()
            del stn_tst, x_tst, x_tst_lengths, sid
            return "Success", (hps.data.sampling_rate, audio)

        return tts_fn
    