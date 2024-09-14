import os
from queue import Queue
import shutil
import threading
import zipfile

import requests
from tqdm import tqdm
from pluginInterface import VtuberPluginInterface
import gradio as gr
from pluginSelectionBase import PluginSelectionBase
import LAV_utils
from pydub import AudioSegment
import simpleaudio as sa


class Vtuber(PluginSelectionBase):
    output_event_listeners = []

    def __init__(self) -> None:
        super().__init__(VtuberPluginInterface)
        self.data = VtuberPluginInterface.AvatarData()

    def create_ui(self):
        with gr.Tab("Vtuber"):
            super().create_plugin_selection_ui()
            super().create_plugin_ui()

    def receive_input(self, normalized_volume):
        self.data.mouth_open = normalized_volume
        current_plugin = self.get_current_plugin()
        if current_plugin is not None:
            current_plugin.set_avatar_data(self.data)
        pass

    def send_output(self, output):
        print(output)
        for subcriber in self.output_event_listeners:
            subcriber(output)

    def add_output_event_listener(self, function):
        self.output_event_listeners.append(function)
