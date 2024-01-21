from queue import Queue
import threading
from pluginInterface import TTSPluginInterface
import gradio as gr
from pluginSelectionBase import PluginSelectionBase
import utils
from pydub import AudioSegment
import simpleaudio as sa


class TTS(PluginSelectionBase):
    input_queue = Queue()
    audio_data_queue = Queue()
    audio_process_thread = None
    audio_playback_thread = None

    def __init__(self) -> None:
        super().__init__(TTSPluginInterface)

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
        return self.current_plugin.synthesize(text)

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

    def play_sound_from_bytes(self, audio_data):
        with open(self.VOICE_OUTPUT_FILENAME, "wb") as file:
            file.write(audio_data)
        audio = AudioSegment.from_wav(self.VOICE_OUTPUT_FILENAME)
        # Convert audio to raw data
        raw_data = audio.raw_data
        num_channels = audio.channels
        bytes_per_sample = audio.sample_width
        sample_rate = audio.frame_rate
        play_obj = sa.play_buffer(raw_data, num_channels,
                                  bytes_per_sample, sample_rate)
        play_obj.wait_done()
