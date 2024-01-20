import gradio as gr
from pluginLoader import plugin_loader
import LLM
from TTS import TTS
import Translate

# load plugins
plugin_loader.load_plugins()

# load ui
with gr.Blocks() as main_interface:

    tts = TTS()

    # LLM.create_ui()
    # Translate.create_ui()
    tts.create_ui()

    # LLM.add_output_event_listener(Translate.receive_input)
    # Translate.add_output_event_listener(tts.receive_input)


main_interface.launch()
