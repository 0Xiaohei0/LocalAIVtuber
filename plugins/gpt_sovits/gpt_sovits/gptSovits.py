import sys
import time
import requests
import os
import subprocess
current_module_directory = os.path.dirname(__file__)
sys.path.append(current_module_directory)
from GPT_SoVITS.api_direct import tts_endpoint



class GptSovits():
    current_module_directory = os.path.dirname(__file__)
    output_dir = os.path.join(current_module_directory, "output.wav")
    server_dir = os.path.join(current_module_directory, "GPT_SoVITS")
    lang = ["zh","en","ja"]
    url = "http://127.0.0.1:9880"

    def init(self):
        pass
    def synthesize(self, text):
        response = tts_endpoint(text=text, text_language='en')

        try:
            with open(self.output_dir, 'wb') as file:
                file.write(response.content)
            print("Audio file downloaded successfully:", self.output_dir)
        except Exception as e:
            print("Failed to download audio file.", e)
            
        return response.content

if __name__ == '__main__':
    gptSovits = GptSovits()

    gptSovits.synthesize("Audio file downloaded successfully, test.")
    complete = True
