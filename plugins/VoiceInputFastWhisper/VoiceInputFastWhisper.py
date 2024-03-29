
import os
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
from transformers import pipeline
import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel
from .languages import LANGUAGES
import torch

class VoiceInputFastWhisper(InputPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    MIC_OUTPUT_PATH = os.path.join(
        current_module_directory, "voice_recording.wav")

    def init(self):
        self.liveTextbox = LiveTextbox()
        # self.transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
        self.mic_mode = 'open mic'
        self.recording = False
        self.input_language = None
        self.ambience_adjusted = False

        # Check if CUDA is available and set the device accordingly
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"torch.cuda.is_available() {torch.cuda.is_available()}")

        model_size = "base"
        self.model = WhisperModel(model_size)
        self.liveTextbox.print(f"fast_whisper.device: {self.device}")

        self.whisper_filter_list = [
            'you', 'thank you.', 'thanks for watching.', "Thank you for watching.", "1.5%"]

    def create_ui(self):
        with gr.Accordion("Voice Input"):
            with gr.Row():
                self.start_listening_button = gr.Button(
                    "start Listening", self.start_listening)
                self.stop_listening_button = gr.Button(
                    "stop Listening", self.stop_listening)
            with gr.Row():
                language_list = list(LANGUAGES.values())
                language_list.insert(0, 'auto')
                self.language_dropdown = gr.Dropdown(language_list, value='auto', label="Input languages")
            with gr.Accordion("Console"):
                self.liveTextbox.create_ui()

        self.start_listening_button.click(self.start_listening)
        self.stop_listening_button.click(self.stop_listening)
        self.language_dropdown.input(self.on_language_change, inputs=[self.language_dropdown])

    def on_language_change(self, choice):
        self.input_language = choice
        self.liveTextbox.print(f"changed language to {choice}")
    

    def start_listening(self):
        gr.Info("starting listening...")
        self.recording = True
        thread = Thread(target=self.transcribe_loop)
        thread.start()
        self.liveTextbox.print("Started listening...")

    def stop_listening(self):
        gr.Info("Stopping listening...")
        self.recording = False
        self.ambience_adjusted = False
        self.liveTextbox.print("Stopped listening...")
        

    def transcribe_loop(self):
        while self.recording:
            self.transcribe()
    def transcribe(self):
        if (self.mic_mode == 'open mic'):
            # record audio
            # obtain audio from the microphone
            r = sr.Recognizer()
            with sr.Microphone() as source:
                if (not self.ambience_adjusted):
                    self.liveTextbox.print("Adjusting for ambient noise...")
                    r.adjust_for_ambient_noise(source)
                    self.ambience_adjusted = True
                self.liveTextbox.print("Say something!")
                audio = r.listen(source)

            if not self.recording:
                return

            with open(self.MIC_OUTPUT_PATH, "wb") as file:
                file.write(audio.get_wav_data())
        elif (self.mic_mode == 'push to talk'):
            pass
            # push_to_talk()
        self.liveTextbox.print("recording compelete, sending to whisper")

        # send audio to whisper
        transcribed_text = ''
        try:
            segments, info = self.model.transcribe(self.MIC_OUTPUT_PATH, beam_size=5)
            print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

            for segment in segments:
                print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                transcribed_text += segment.text
            
        except sr.UnknownValueError:
            self.liveTextbox.print("Whisper could not understand audio")
        except sr.RequestError as e:
            self.liveTextbox.print("Could not request results from Whisper")
        if (transcribed_text == ''):
            return

        print(
            f'looking for {transcribed_text.strip().lower()} in {self.whisper_filter_list}')
        if (transcribed_text.strip().lower() in self.whisper_filter_list):
            self.liveTextbox.print(f'Input {transcribed_text} was filtered.')
            return
        self.liveTextbox.print(f"transcribed output: {transcribed_text}")
        self.process_input(transcribed_text)
