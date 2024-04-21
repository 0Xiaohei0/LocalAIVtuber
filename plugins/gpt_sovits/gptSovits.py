import requests
import os
import gradio as gr
from pluginInterface import TTSPluginInterface
import subprocess



class gptSovits(TTSPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    output_dir = os.path.join(current_module_directory, "output.wav")
    server_dir = os.path.join(current_module_directory, "GPT_SoVITS")
    lang = ["zh","en","ja"]
    url = "http://127.0.0.1:9880"

    def init(self):
        self.language = self.lang[1]
        command = [
        "python", "api.py",
        "-s", r"./SoVITS_weights/kokomi2_e15_s2295.pth",
        "-g", r"./GPT_weights/kokomi2-e10.ckpt",
        "-dr", r"./ふーん、新作対戦ゲーム設置しました、か.mp3",
        "-dt", "ふーん、新作対戦ゲーム設置しました、か",
        "-dl", "ja"
        ]

        # command = [
        # "python", "api.py",
        # "-s", r"./SoVITS_weights/kokomi2_e15_s2295.pth",
        # "-g", r"./GPT_weights/kokomi2-e10.ckpt",
        # "-dr", r"./vo_card_kokomi_freetalk_01.wav",
        # "-dt", "The situation is ever-changing in a card game. To emerge victorious, you have to be willing to take some risks.",
        # "-dl", "en"
        # ]

        # command = [
        # "python", "api.py",
        # "-s", r"./SoVITS_weights/nene60_test_e8_s280.pth",
        # "-g", r"./GPT_weights/nene60-test-e20.ckpt",
        # "-dr", r"./sample.mp3",
        # "-dt", "ふーん、新作対戦ゲーム設置しました、か",
        # "-dl", "ja"
        # ]
        print(f"process = subprocess.Popen({command}, cwd={self.server_dir}, shell=True)")
        process = subprocess.Popen(command, cwd=self.server_dir, shell=True)
        print(f"GPT-Sovits Server started with PID {process.pid}")

    def synthesize(self, text):
        params = {
            'text': text,
            'text_language': self.language
        }
        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            with open(self.output_dir, 'wb') as file:
                file.write(response.content)
            print("Audio file downloaded successfully:", self.output_dir)
        else:
            print("Failed to download audio file. Status Code:", response.status_code)
            
        return response.content


    def create_ui(self):
        with gr.Accordion(label="gpt-sovits Options", open=False):
            with gr.Row():
                self.language_dropdown = gr.Dropdown(choices=self.lang, value=self.language, label='language')
                
        self.language_dropdown.change(self.update_language, inputs=[self.language_dropdown])
    
    def update_language(self, input):
        self.language = input
    
    