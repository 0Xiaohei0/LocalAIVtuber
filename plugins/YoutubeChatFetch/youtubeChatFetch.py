from queue import Queue
import threading
import traceback
import pytchat
import time
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
from globals import global_state, GlobalKeys
import LAV_utils

class YoutubeChatFetch(InputPluginInterface):
    read_chat_youtube_thread = None
    read_chat_youtube_thread_running = False

    excluded_users_list = []
    liveTextbox = LiveTextbox()
    console_textbox = LiveTextbox()
    queue_textbox = LiveTextbox()
    chatlog = Queue(maxsize=3)
    chat_process_thread = None
    prompt_format = "a viewer named ([name]) send message ([message]) to stream chat. Repeat the message and then your response."
    def create_ui(self):
        with gr.Accordion(label="Youtube Chat Fetch", open=False):
            with gr.Row():
                self.youtube_video_id_textbox = gr.Textbox(
                    label="youtube_video_id", show_label=True)
                self.start_fetch_button = gr.Button("Start Fetching Chat")
                self.stop_fetch_button = gr.Button("Stop Fetching Chat")
                self.prompt_format_textbox = gr.Textbox(label= "Prompt format")

                self.start_fetch_button.click(self.read_chat_youtube, inputs=[
                                              self.youtube_video_id_textbox])
                self.stop_fetch_button.click(self.stop_read_chat_youtube)

                self.prompt_format_textbox.change(fn=self.update_prompt, inputs=self.prompt_format_textbox)
            self.liveTextbox.create_ui()
            self.console_textbox.create_ui()
            self.queue_textbox.create_ui()


    def update_prompt(self, text):
        self.prompt_format = text
    def read_chat_youtube(self, youtube_video_id):
        gr.Info("starting chat fetching...")
        # print("starting chat fetching...")
        chat = None
        try:
            chat = pytchat.create(
                video_id=youtube_video_id, interruptable=False, topchat_only=True)
        except:
            print("failed to fetch chat")
            print(traceback.format_exc())
            return
        self.read_chat_youtube_thread = Thread(
            target=self.read_chat_loop, args=[chat,])
        self.read_chat_youtube_thread.start()
        self.read_chat_youtube_thread_running = True

    def read_chat_loop(self, chat):
        print("Chat fetching started")
        self.liveTextbox.print("Chat fetching started")
        while self.read_chat_youtube_thread_running and chat.is_alive():
            for c in chat.get().sync_items():
                if c.author.name not in self.excluded_users_list:
                    # print(f"{c.datetime} [{c.author.name}]- {c.message}")
                    self.read_chat_loop
                    self.liveTextbox.print(
                        f"{c.datetime} [{c.author.name}]- {c.message}")
                    self.add_to_chat_log(c.author.name, c.message)
            time.sleep(5)
        print("Chat fetching ended")
        self.liveTextbox.print("Chat fetching started")

    def stop_read_chat_youtube(self):
        gr.Info("stopping chat fetching...")
        print("stopping chat fetching...")
        self.read_chat_youtube_thread_running = False
        # print("Process stopped.")
        self.liveTextbox.print("Process stopped.")

    
    def add_to_chat_log(self, author, message):
        if self.chatlog.full():
            self.chatlog.get()
        
        self.chatlog.put([author, message])
        self.process_chat_log()

    def process_chat_log(self):
        def generate_response():
            while (not self.chatlog.empty()):
                self.queue_textbox.set(LAV_utils.queue_to_list(self.chatlog))
                if(global_state.get_value(GlobalKeys.IS_IDLE)):
                    input = self.chatlog.get()
                    prompt = self.prompt_format.replace("[name]", input[0]).replace("[message]", input[1])
                    self.process_input(prompt)
                    self.console_textbox.print(f"Sending: {prompt}")
                    self.queue_textbox.set(LAV_utils.queue_to_list(self.chatlog))
                time.sleep(5)    

        # Check if the current thread is alive
        if self.chat_process_thread is None or not self.chat_process_thread.is_alive():
            # Create and start a new thread
            self.chat_process_thread = threading.Thread(target=generate_response)
            self.chat_process_thread.start()
