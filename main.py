import os
import threading
import gradio as gr
from pluginLoader import plugin_loader
from Input import Input
from LLM import LLM
from TTS import TTS
from VTuber import Vtuber
from Translate import Translate
from globals import global_state, GlobalKeys

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

global_update_loop = None

def update_globals():
    global global_update_loop
    try:
        update_globals_periodic()
    except KeyboardInterrupt:
        print("Stopping...")
        if global_update_loop: global_update_loop.cancel()

def update_globals_periodic():
    global_state.set_value(GlobalKeys.IS_IDLE, llm.input_queue.empty() and translate.input_queue.empty() and tts.input_queue.empty() and tts.audio_data_queue.empty())
    #print(f"global_state.get_value(GlobalKeys.IS_IDLE) {global_state.get_value(GlobalKeys.IS_IDLE)}")
    global global_update_loop
    global_update_loop = threading.Timer(0.5, update_globals_periodic).start()

update_globals()
main_interface.queue().launch()



