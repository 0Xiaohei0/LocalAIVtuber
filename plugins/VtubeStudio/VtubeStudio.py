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

    def init(self):
        pass

    def create_ui(self):
        with gr.Accordion(label="Vtube Studio Options", open=False):
            with gr.Row():
                self.authenticate_button = gr.Button("Authenticate")
        self.authenticate_button.click(self.on_authenticate_click)

    def on_authenticate_click(self):
        gr.Info("Aquiring token, please continue in Vtube Studio...")
        thread = threading.Thread(target=self.websocket_thread)
        thread.start()

    def authenticate(self):
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
        self.authenticate()

    def on_message(self, ws, message):
        print("Received message:", message)
        response = json.loads(message)

        if response['messageType'] == "AuthenticationTokenResponse":
            self.token = response['data']['authenticationToken']
            print("Authentication token received:", self.token)
            self.send_authentication_request()
        elif response['messageType'] == "AuthenticationResponse":
            self.token = response['data']['authenticationToken']
            print("Authentication token received:", self.token)
            self.send_authentication_request()

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

    def websocket_thread(self):
        self.ws = websocket.WebSocketApp("ws://localhost:8001",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()
