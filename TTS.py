from queue import Queue
import threading
from pluginLoader import plugin_loader
from pluginInterface import TTSPluginInterface
import gradio as gr
import utils
from pydub import AudioSegment
import simpleaudio as sa

selected_provider = None
input_queue = Queue()
audio_data_queue = Queue()
audio_process_thread = None
audio_playback_thread = None


def create_ui():
    category_name = plugin_loader.interface_to_category[TTSPluginInterface]
    TTSProviderList, TTSProviderMap = utils.pluginToNameMap(
        plugin_loader.plugins[category_name])
    default_provider_name = TTSProviderList[0] if TTSProviderList else None
    global selected_provider
    selected_provider = TTSProviderMap[default_provider_name]
    load_provider()
    with gr.Tab("TTS"):
        gr.Dropdown(
            choices=TTSProviderList,
            value=default_provider_name,
            type="value",
            label="TTS provider: ",
            info="Select the text to speech provider",
            interactive=True)
        gr.Interface(
            fn=selected_provider.synthesize,
            inputs=[gr.Textbox(label="Original Text")],
            outputs=[gr.Audio(label="Synthesized Voice")],
            allow_flagging="never",
            examples=["すぅ…はぁ——おはようさん、朝の空気は清々しくて気持ちええなぁ、深呼吸して頭もすっきりや。",
                      "金魚飼ったことある？大人しゅうて、めっちゃ可愛ええんや。",
                      "全身ポカポカで気持ちええわぁ～、浮いとるみたい。"]
        )
        selected_provider.create_ui()


def load_provider():
    global selected_provider
    if issubclass(type(selected_provider), TTSPluginInterface):
        print("Loading TTS Module...")
        selected_provider.init()


VOICE_OUTPUT_FILENAME = "synthesized_voice.wav"


def preprocess_input(text):
    text = text.replace(" ", "")
    return text


def receive_input(text):
    text = preprocess_input(text)
    input_queue.put(text)
    process_input_queue(selected_provider.synthesize)


def process_input_queue(function):
    def generate_audio():
        while (not input_queue.empty()):
            # generate audio data and queue up for playing
            audio_data_queue.put(function(input_queue.get()))
            process_audio_queue(play_sound_from_bytes)

    global audio_process_thread
    # Check if the current thread is alive
    if audio_process_thread is None or not audio_process_thread.is_alive():
        # Create and start a new thread
        audio_process_thread = threading.Thread(target=generate_audio)
        audio_process_thread.start()


def process_audio_queue(function):
    def play_audio():
        while (not audio_data_queue.empty()):
            # generate audio data and queue up for playing
            function(audio_data_queue.get())

    global audio_playback_thread
    # Check if the current thread is alive
    if audio_playback_thread is None or not audio_playback_thread.is_alive():
        # Create and start a new thread
        audio_playback_thread = threading.Thread(target=play_audio)
        audio_playback_thread.start()


def play_sound_from_bytes(audio_data):
    with open(VOICE_OUTPUT_FILENAME, "wb") as file:
        file.write(audio_data)
    audio = AudioSegment.from_wav(VOICE_OUTPUT_FILENAME)
    # Convert audio to raw data
    raw_data = audio.raw_data
    num_channels = audio.channels
    bytes_per_sample = audio.sample_width
    sample_rate = audio.frame_rate
    play_obj = sa.play_buffer(raw_data, num_channels,
                              bytes_per_sample, sample_rate)
    play_obj.wait_done()
