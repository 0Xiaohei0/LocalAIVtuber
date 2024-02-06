import inspect
from pluginInterface import InputPluginInterface
import gradio as gr
from pluginSelectionBase import PluginSelectionBase
import os


class Input(PluginSelectionBase):
    def __init__(self) -> None:
        super().__init__(InputPluginInterface)
        self.current_plugin.input_event_listeners.append(self.send_output)
        self.output_event_listeners = []

    def create_ui(self):
        with gr.Tab("Input"):
            with gr.Blocks():
                super().create_plugin_selection_ui()

            super().create_plugin_ui()

    def send_output(self, output):
        print(output)
        for subcriber in self.output_event_listeners:
            subcriber(output)

    def add_output_event_listener(self, function):
        self.output_event_listeners.append(function)
