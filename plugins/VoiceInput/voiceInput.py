
import os
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
from transformers import pipeline
import numpy as np
import speech_recognition as sr
import whisper
from .languages import LANGUAGES
from eventManager import event_manager, EventType
import keyboard

class VoiceInput(InputPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    MIC_OUTPUT_PATH = os.path.join(
        current_module_directory, "voice_recording.wav")

    key_to_bind = "ctrl+a"  # Default binding

    def init(self):
        self.liveTextbox = LiveTextbox()
        # self.transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
        self.mic_mode = 'open mic'
        self.recording = False
        self.input_language = "english"
        self.ambience_adjusted = False

        self.model = whisper.load_model("small.en")
        self.liveTextbox.print(f"whisper_model.device: {self.model.device}")
        self.whisper_filter_list = [
            'you', 'thank you.', 'thanks for watching.', "Thank you for watching.", "1.5%", "I'm going to put it in the fridge.", "I", ".", "okay.", "bye.", "so,"]
        
        # Assign the function to be called when the space bar is pressed
        keyboard.add_hotkey(self.key_to_bind, self.on_interrupt_key)

    def create_ui(self):
        with gr.Accordion("Voice Input",open=False):
            with gr.Row():
                self.start_listening_button = gr.Button(
                    "start Listening", self.start_listening)
                self.stop_listening_button = gr.Button(
                    "stop Listening", self.stop_listening)
            with gr.Row():
                language_list = list(LANGUAGES.values())
                language_list.insert(0, 'auto')
                self.language_dropdown = gr.Dropdown(language_list, value=self.input_language, label="Input languages")
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
            audio = whisper.load_audio(self.MIC_OUTPUT_PATH)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            options = whisper.DecodingOptions(task='transcribe', language=self.input_language,
                                              without_timestamps=True, fp16=False if self.model.device == 'cpu' else None)
            result = whisper.decode(self.model, mel, options)
            transcribed_text = result.text
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

    def on_interrupt_key(self):
        print(f"You pressed the '{self.key_to_bind}' key!")
        event_manager.trigger(EventType.INTERRUPT)

