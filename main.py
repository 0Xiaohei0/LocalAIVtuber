import gradio as gr
from pluginLoader import plugin_loader
import LLM
import TTS
import Translate

# load plugins
plugin_loader.load_plugins()

# load ui
with gr.Blocks() as demo:
    LLM.create_ui()
    Translate.create_ui()
    TTS.create_ui()

    # LLM.add_output_event_listener(Translate.input)

demo.launch()
