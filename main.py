import os
import gradio as gr
from pluginLoader import plugin_loader
from Input import Input
from LLM import LLM
from TTS import TTS
from VTuber import Vtuber
from Translate import Translate

import logging

logging.basicConfig(level=logging.WARNING)

# allow relative imports in plugins folder
import sys
current_module_directory = os.path.dirname(__file__)
plugin_directory = os.path.join(current_module_directory, "plugins")
sys.path.append(plugin_directory)

# load plugins
plugin_loader.load_plugins()

# load ui
with gr.Blocks() as main_interface:
    input = Input()
    llm = LLM()
    translate = Translate()
    tts = TTS()
    vtuber = Vtuber()

    input.create_ui()
    llm.create_ui()
    translate.create_ui()
    tts.create_ui()
    vtuber.create_ui()

    input.add_output_event_listener(llm.receive_input)
    llm.add_output_event_listener(translate.receive_input)
    translate.add_output_event_listener(tts.receive_input)
    tts.add_output_event_listener(vtuber.receive_input)

main_interface.queue().launch()
