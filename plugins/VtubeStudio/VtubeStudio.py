import subprocess
import time
import zipfile
import gradio as gr
import requests
from tqdm import tqdm
from pluginInterface import VtuberPluginInterface
import os


class VtubeStudio(VtuberPluginInterface):

    def init(self):
        pass

    def create_ui(self):
        with gr.Accordion(label="Vtube Studio Options", open=False):
            with gr.Row():
                pass
