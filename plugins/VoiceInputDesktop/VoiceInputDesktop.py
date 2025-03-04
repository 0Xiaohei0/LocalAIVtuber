import os
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
from .languages import LANGUAGES
import asyncio
import os
import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, WebSocket
from silero_vad import load_silero_vad, VADIterator
from faster_whisper import WhisperModel
import wave


class VoiceInputDesktop(InputPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    MIC_OUTPUT_PATH = os.path.join(
        current_module_directory, "voice_recording.wav")

    SAMPLING_RATE = 16000
    input_language = "en"
    whisper_filter_list = [
                'you', 'thank you.', 'thanks for watching.', "Thank you for watching.", "1.5%", "I'm going to put it in the fridge.", "I", ".", "okay.", "bye.", "so,", "I'm sorry."]
    SPEECH_THRESHOLD = 0.3
    SILENCE_WAIT_TIME = 0.5 * SAMPLING_RATE 
    PRE_SPEECH_SAMPLES = 0.5 * SAMPLING_RATE  
    POST_SPEECH_SAMPLES = 0.5 * SAMPLING_RATE  

    app = FastAPI()
    vad_model = load_silero_vad()
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    whisper_model = WhisperModel("small", device=device) # Load Whisper model    
    server_thread = None

    def init(self):
        self.liveTextbox = LiveTextbox()
        self.server_thread = Thread(target=self.run_websocket_server)
        self.server_thread.start()

    def run_websocket_server(self):
        uvicorn.run(self.app, host="127.0.0.1", port=8000)

    def create_ui(self):
        with gr.Accordion("Voice Input",open=False):
            with gr.Row():
                language_list = list(LANGUAGES.keys())
                language_list.insert(0, 'auto')
                self.language_dropdown = gr.Dropdown(language_list, value=self.input_language, label="Input languages")
            with gr.Accordion("Console"):
                self.liveTextbox.create_ui()

        self.language_dropdown.input(self.on_language_change, inputs=[self.language_dropdown])

    def on_language_change(self, choice):
        self.input_language = choice
        self.liveTextbox.print(f"changed language to {choice}")

    def process_audio(self, audio_np):
        vad_iterator = VADIterator(self.vad_model, sampling_rate=self.SAMPLING_RATE)
        sentence_audio_buffer = []
        tmp_audio_buffer = []
        silent_samples = 0
        started_speaking = False

        tmp_audio_buffer.extend(audio_np)

        while len(tmp_audio_buffer) >= 512:
            chunk = np.array(tmp_audio_buffer[:512])  # Extract first 512 samples
            tmp_audio_buffer = tmp_audio_buffer[512:]  # Remove processed chunk

            # Run VAD on the chunk
            speech_prob = self.vad_model(torch.from_numpy(chunk), self.SAMPLING_RATE).item()

            if speech_prob < self.SPEECH_THRESHOLD:
                if silent_samples <= self.SILENCE_WAIT_TIME:
                    silent_samples += 512
            else:
                silent_samples = 0
                if not started_speaking:
                    # Capture pre-speech samples
                    pre_speech_samples = sentence_audio_buffer[-int(self.PRE_SPEECH_SAMPLES):]
                    sentence_audio_buffer = list(pre_speech_samples)
                started_speaking = True

            if started_speaking:
                sentence_audio_buffer.extend(chunk)

            if started_speaking and silent_samples > self.SILENCE_WAIT_TIME:  # 2 seconds of silence
                print("User finished speaking! Sending to STT...")
                # Capture post-speech samples
                post_speech_samples = tmp_audio_buffer[:int(self.POST_SPEECH_SAMPLES)]
                sentence_audio_buffer.extend(post_speech_samples)
                transcribed_text = self.process_speech(np.array(sentence_audio_buffer))  # Process audio
                print(f"transcribed_text {transcribed_text}")
                self.process_input(transcribed_text)
                vad_iterator.reset_states()  # Reset VAD for next detection
                tmp_audio_buffer = []  # Clear buffer
                sentence_audio_buffer = [] 
                silent_samples = 0
                started_speaking = False

    @app.websocket("/audio-stream")
    async def websocket_audio_stream(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            audio_bytes = await websocket.receive_bytes()
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0  # Convert PCM to float
            self.process_audio(audio_np)

    def process_speech(self, audio_data):
        with wave.open(self.MIC_OUTPUT_PATH, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes((audio_data * 32768.0).astype(np.int16).tobytes())

        transcribed_text = ''
        segments, _  = self.whisper_model.transcribe(self.MIC_OUTPUT_PATH, language=self.input_language)  # Updated transcription
        segments = list(segments)
        for segment in segments:
            transcribed_text += segment.text
        if (transcribed_text == ''):
            return

        if (transcribed_text.strip().lower() in self.whisper_filter_list):
            return
        return transcribed_text
