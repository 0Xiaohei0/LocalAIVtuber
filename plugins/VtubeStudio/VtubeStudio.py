import json
import subprocess
import threading
import time
import zipfile
import gradio as gr
import requests
from tqdm import tqdm
import websocket
from pluginInterface import VtuberPluginInterface
import os


class VtubeStudio(VtuberPluginInterface):
    isAuthenticated = False
    token = ""
    current_module_directory = os.path.dirname(__file__)
    token_path = os.path.join(
        current_module_directory, "token.txt")
    current_volume = 0

    def init(self):
        self.authenticate()

    def create_ui(self):
        with gr.Accordion(label="Vtube Studio Options", open=False):
            with gr.Row():
                self.authenticate_button = gr.Button("Authenticate")
        self.authenticate_button.click(self.on_authenticate_click)

    def on_authenticate_click(self):
        self.authenticate()

    def authenticate(self):
        if not os.path.exists(self.token_path):
            gr.Info("Aquiring token, please continue in Vtube Studio...")
        else:
            gr.Info("Token Found, attempting to authenticate with token...")
        thread = threading.Thread(target=self.websocket_thread)
        thread.start()

    def getToken(self):
        token_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "123",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": "LocalAIVtuberPlugin",
                "pluginDeveloper": "Xiaohei"
            }
        }
        self.ws.send(json.dumps(token_request))

    def on_open(self, ws):
        # Check if the file exists. If not, create an empty file.
        if not os.path.exists(self.token_path):
            with open(self.token_path, 'w') as file:
                file.write('')
            self.getToken()

        else:
            with open(self.token_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.token = content
            self.send_authentication_request()

    def on_message(self, ws, message):
        response = json.loads(message)
        if response['messageType'] == "InjectParameterDataResponse":
            return
        print("Received message:", message)
        if response['messageType'] == "AuthenticationTokenResponse":
            self.token = response['data']['authenticationToken']
            print("Authentication token received:", self.token)
            with open(self.token_path, 'w') as file:
                file.write(self.token)
            self.send_authentication_request()
            return
        if response['messageType'] == "AuthenticationResponse":
            self.token = response['data']['authenticated'] == True
            print(response['data']['reason'])
            threading.Thread(target=self.mouth_data_thread).start()
            return

    def send_authentication_request(self):
        auth_request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "234",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": "LocalAIVtuberPlugin",
                "pluginDeveloper": "Xiaohei",
                "authenticationToken": self.token
            }
        }
        self.ws.send(json.dumps(auth_request))

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### Connection closed ###")
        print("Failed to connect to vtube studio, if you want vtube studio functionalities, please start vtube studio and enable plugins.")

    def websocket_thread(self):
        self.ws = websocket.WebSocketApp("ws://localhost:8001",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

    def mouth_data_thread(self):
        while True:
            #print(f"Setting MouthOpen to {self.avatar_data.mouth_open}")
            message = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "2",
                "messageType": "InjectParameterDataRequest",
                "data": {
                    "mode": "set",
                    "parameterValues": [
                        {
                            "id": "MouthOpen",
                            "value": self.avatar_data.mouth_open
                        },
                    ]
                }
            }
            self.ws.send(json.dumps(message))
            time.sleep(0.1)
