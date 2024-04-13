import os
from threading import Thread
import threading
import time
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
import socket

class OtherLLM(InputPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    start_port, end_port = 2300, 2302
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_port = 2300
    client_port = 2301

    connected = False
    def init(self):
        self.liveTextbox = LiveTextbox()
        
        self.socket_listen()
        self.socket_connect()

    def create_ui(self):
        with gr.Blocks() as ui:
            with gr.Accordion("OtherLLM Connection",open=False):
                with gr.Row():
                    self.connect_button = gr.Button("Connect")
                with gr.Row():
                    self.send_button = gr.Button("Send")
                    self.message_textbox = gr.Textbox(label="Message", placeholder="Type message here...", show_label=False)
                with gr.Accordion("Console"):
                    self.liveTextbox.create_ui()

            self.connect_button.click(fn=self.socket_connect)

            self.send_button.click(
                fn=self.send_data,
                inputs=[self.message_textbox])
            
    def find_free_port(self):
        for port in range(self.start_port, self.end_port):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', port))
                s.listen(1)
                return s, port
            except socket.error:
                continue
        raise IOError("No free ports available")

    # start server
    def socket_listen(self):
        try:
            self.liveTextbox.print(f"Starting host")
            self.server_socket, self.server_port = self.find_free_port()
            Thread(target=self.accept_connections).start()
            self.liveTextbox.print(f"host started on {self.server_port}")
        except Exception as e:
            print(f"Failed to listen {str(e)}")
            self.liveTextbox.print(f"Failed to listen on port {str(e)}")

    def accept_connections(self):
        while True:
            try:
                client, addr = self.server_socket.accept()
                Thread(target=self.handle_client, args=(client,)).start()
            except Exception as e:
                print(f"Error accepting connections: {str(e)}")
                break

    def handle_client(self, client):
        while True:
            try:
                data = client.recv(1024)
                if data:
                    print(f"Received: {data.decode()}")
                    self.liveTextbox.print(f"Received: {data.decode()}")  # Assuming LiveTextbox has such a method
                else:
                    print("No data received. Closing connection.")
                    client.close()
                    break
            except Exception as e:
                print(f"Error handling client data: {str(e)}")
                client.close()
                break

    def socket_connect(self):
        for port in range(self.start_port, self.end_port):
            try:
                if(port == self.server_port): continue
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(('localhost', port))
                self.client_port = port
                self.liveTextbox.print(f"Connected to port{port}")
                return
            except socket.error:
                continue
        
        Thread(target=self.retry_connect).start()

    def retry_connect(self):
        for port in range(self.start_port, self.end_port):
            try:
                if(port == self.server_port): continue
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(('localhost', port))
                self.client_port = port
                self.liveTextbox.print(f"Connected to port{port}")
                return
            except socket.error:
                continue
        
        time.sleep(1)
        self.retry_connect()


    def send_data(self, message):
        try:
            self.client_socket.sendall(message.encode())
            print(f"Sent: {message}")  # Optionally print the sent message to console or UI
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
