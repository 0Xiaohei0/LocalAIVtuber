import gradio as gr
from pluginLoader import plugin_loader
import LLM
from TTS import TTS
from Translate import Translate

# load plugins
plugin_loader.load_plugins()

# load ui
with gr.Blocks() as main_interface:
    # llm = LLM()
    translate = Translate()
    tts = TTS()

    # llm.create_ui()
    translate.create_ui()
    tts.create_ui()

    # LLM.add_output_event_listener(Translate.receive_input)
    translate.add_output_event_listener(tts.receive_input)


main_interface.launch()
