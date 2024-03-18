import traceback
import pytchat
import time
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
from transformers import pipeline
import numpy as np

class VoiceInput(InputPluginInterface):
    liveTextbox = LiveTextbox()
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

    def create_ui(self):
        with gr.Accordion(label="Voice Input", open=False):
            demo = gr.Interface(
                self.transcribe,
                ["state", gr.Audio(sources=["microphone"], streaming=True)],
                ["state", "text"],
                live=True,
            )
            # with gr.Row():
            #     self.start_listening_button = gr.Button("Start Listening")
            #     self.stop_listening_button = gr.Button("Stop Listening")

            #     self.start_listening_button.click(self.start_listening)
            #     self.stop_listening_button.click(self.stop_listening)
            with gr.Accordion("Console"):
                self.liveTextbox.create_ui()
    def start_listening(self):
        gr.Info("starting listening...")
    

    def stop_listening(self):
        gr.Info("Stopped listening...")
        self.liveTextbox.print("Process stopped.")



    def transcribe(self, stream, new_chunk):
        sr, y = new_chunk
        
        # Check if the audio is not mono (single channel), convert it to mono by averaging the channels
        if y.ndim > 1 and y.shape[1] > 1:  # This checks if y is multi-dimensional and has more than one channel
            y = np.mean(y, axis=1)  # Averages the channels to convert to mono
        
        y = y.astype(np.float32)
        y /= np.max(np.abs(y), axis=0, keepdims=True) + 1e-9  # Normalizing, also added a small number to avoid division by zero

        if stream is not None:
            stream = np.concatenate([stream, y])
        else:
            stream = y

        # Assuming self.transcriber is an instance of AutomaticSpeechRecognitionPipeline
        return stream, self.transcriber({"sampling_rate": sr, "raw": stream})["text"]

