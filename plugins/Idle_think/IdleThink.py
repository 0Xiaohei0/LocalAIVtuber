from enum import Enum, auto
import json
import threading
import traceback
import pytchat
import time
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
import requests
from globals import GlobalKeys, global_state

class IdleThink(InputPluginInterface):
    
    console_textbox = LiveTextbox()
    idle_elapsed_time = 0
    idle_dialog_trigger_time = 20

    def init(self):
        self.monitor_thread = threading.Thread(target=self.monitor_value)
        self.monitor_thread.start()
    
    def create_ui(self):
        with gr.Accordion(label="Idle Think", open=False):
            with gr.Row():
                self.Idle_interval_textbox = gr.Textbox(label="Idle interval",value=self.idle_dialog_trigger_time)
                
            self.console_textbox.create_ui()
            self.Idle_interval_textbox.change(fn=self.update_idle_interval, inputs=self.Idle_interval_textbox)

    def update_idle_interval(self, interval):
        self.idle_dialog_trigger_time = float(interval)
        self.console_textbox.print(f"Updating Idle interval  to {self.idle_dialog_trigger_time}")

    def monitor_value(self):
        while True:
            self.console_textbox.print(f"global_state.get_value(GlobalKeys.IS_IDLE) {global_state.get_value(GlobalKeys.IS_IDLE)}")
            if global_state.get_value(GlobalKeys.IS_IDLE):
                if self.start_time is None:
                    self.start_time = time.time()
                elif time.time() - self.start_time >= self.idle_dialog_trigger_time:
                    self.trigger_function()
                    self.start_time = None  # Reset the timer after action
                if self.start_time:
                    self.console_textbox.print(f"Idle for {time.time() - self.start_time} / {self.idle_dialog_trigger_time}")
            else:
                self.start_time = None  # Reset the timer if value changes
            time.sleep(0.5)  # Polling interval

    def trigger_function(self):
        print(f"Idle for {self.idle_dialog_trigger_time}, sending idle dialogue")
        self.console_textbox.print(f"Idle for {self.idle_dialog_trigger_time}, sending idle dialogue")
        self.process_input("Describe a random thought you have. Do not repeat previous thoughts.")
