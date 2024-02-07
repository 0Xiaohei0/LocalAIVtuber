import traceback
import pytchat
import time
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox


class YoutubeChatFetch(InputPluginInterface):
    read_chat_youtube_thread = None
    read_chat_youtube_thread_running = False

    excluded_users_list = []
    liveTextbox = LiveTextbox()

    def create_ui(self):
        with gr.Accordion(label="Youtube Chat Fetch", open=False):
            with gr.Row():
                self.youtube_video_id_textbox = gr.Textbox(
                    label="youtube_video_id", show_label=True)
                self.start_fetch_button = gr.Button("Start Fetching Chat")
                self.stop_fetch_button = gr.Button("Stop Fetching Chat")

                self.start_fetch_button.click(self.read_chat_youtube, inputs=[
                                              self.youtube_video_id_textbox])
                self.stop_fetch_button.click(self.stop_read_chat_youtube)
            self.liveTextbox.create_ui()

    def read_chat_youtube(self, youtube_video_id):
        gr.Info("starting chat fetching...")
        print("starting chat fetching...")
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
                    print(f"{c.datetime} [{c.author.name}]- {c.message}")
                    self.liveTextbox.print(
                        f"{c.datetime} [{c.author.name}]- {c.message}")
                    self.process_input(c.message)
                    time.sleep(1)
        print("Chat fetching ended")

    def stop_read_chat_youtube(self):
        gr.Info("stopping chat fetching...")
        print("stopping chat fetching...")
        self.read_chat_youtube_thread_running = False
        print("Process stopped.")
        self.liveTextbox.print("Process stopped.")
