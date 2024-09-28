import asyncio
import os
from threading import Thread
import threading
import time
import traceback
from twitchio.ext import commands
from liveTextbox import LiveTextbox
from pluginInterface import InputPluginInterface
import gradio as gr
from queue import Queue
from globals import global_state, GlobalKeys
import LAV_utils as utils

class TwitchChatFetch(InputPluginInterface):
    twitchbot = None
    read_chat_twitch_thread = None
    read_chat_twitch_thread_running = False
    loop = None

    twitch_access_token = ""
    twitch_channel_name = ""
    liveTextbox = LiveTextbox()
    console_textbox = LiveTextbox()
    queue_textbox = LiveTextbox()
    chatlog = Queue(maxsize=3)
    chat_process_thread = None
    prompt_format = "a viewer named ([name]) send message ([message]) to stream chat. Repeat the message and then your response."
    
    def init(self):
        pass

    def create_ui(self):
        with gr.Accordion(label="Twitch Chat Fetch", open=False):
            with gr.Row():
                self.twitch_access_token_textbox = gr.Textbox(
                    label="twitch_access_token", show_label=True, info="generate bot chat token here: https://twitchtokengenerator.com/")
                self.twitch_channel_name_textbox = gr.Textbox(
                    label="twitch_channel_name", show_label=True)
                
                self.start_fetch_button = gr.Button("Start Fetching Chat")
                self.stop_fetch_button = gr.Button("Stop Fetching Chat")

                self.start_fetch_button.click(self.read_chat_twitch, inputs=[
                                              self.twitch_access_token_textbox,
                                              self.twitch_channel_name_textbox])
                self.stop_fetch_button.click(self.stop_read_chat_twitch)

            with gr.Row():
                self.prompt_format_textbox = gr.Textbox(label= "Prompt format", value=self.prompt_format)
                self.prompt_format_textbox.change(fn=self.update_prompt, inputs=self.prompt_format_textbox)
            self.liveTextbox.create_ui()
            self.console_textbox.create_ui()
            self.queue_textbox.create_ui()


    def update_prompt(self, text):
        self.prompt_format = text

    def read_chat_twitch(self, twitch_access_token, twitch_channel_name):
        self.twitch_access_token = twitch_access_token
        self.twitch_channel_name = twitch_channel_name
        self.read_chat_twitch_thread = Thread(target=self.runbot)
        self.read_chat_twitch_thread.start()
        self.read_chat_twitch_thread_running = True

    def runbot(self):
        print("Chat fetching started")
        self.liveTextbox.print("Chat fetching started")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.twitchbot = self.Bot(self.twitch_access_token, [self.twitch_channel_name], self)
        self.loop.run_until_complete(self.twitchbot.start())

    def stop_read_chat_twitch(self):
        print("Stopping chat fetch.")
        self.liveTextbox.print("Stopping chat fetch.")
        
        async def close_twitchbot():
            await self.twitchbot.close()
        
        self.loop.call_soon_threadsafe(asyncio.create_task, close_twitchbot())

    def add_to_chat_log(self, author, message):
        if self.chatlog.full():
            self.chatlog.get()
        
        self.chatlog.put([author, message])
        self.process_chat_log()

    def process_chat_log(self):
        def generate_response():
            while (not self.chatlog.empty()):
                self.queue_textbox.set(utils.queue_to_list(self.chatlog))
                if(global_state.get_value(GlobalKeys.IS_IDLE)):
                    input = self.chatlog.get()
                    prompt = self.prompt_format.replace("[name]", input[0]).replace("[message]", input[1])
                    self.process_input(prompt)
                    self.console_textbox.print(f"Sending: {prompt}")
                    self.queue_textbox.set(utils.queue_to_list(self.chatlog))
                time.sleep(5)    

        # Check if the current thread is alive
        if self.chat_process_thread is None or not self.chat_process_thread.is_alive():
            # Create and start a new thread
            self.chat_process_thread = threading.Thread(target=generate_response)
            self.chat_process_thread.start()



    class Bot(commands.Bot):
        current_module_directory = os.path.dirname(__file__)
        excluded_users_file = os.path.join(current_module_directory, "excluded_users.txt")
        excluded_users_list = []

        def __init__(self, token, initial_channels, twitch_chat_fetch):
            # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
            super().__init__(token=token,
                            prefix='?', initial_channels=initial_channels)
            self.twitch_chat_fetch = twitch_chat_fetch
            # Function to reload the excluded users from the file
            reload_thread = Thread(target=self.reload_excluded_users)
            reload_thread.start()

        def reload_excluded_users(self):
            while True:
                try:
                    file_path = self.excluded_users_file
                    with open(file_path, "r") as file:
                        content = file.read()
                        self.excluded_users_list = content.split("\n")
                except:
                    print(f"Unable to load {file_path}.")
                    print(traceback.format_exc())
                time.sleep(10)  # Sleep for 30 seconds before reloading

        async def event_ready(self):
            # We are logged in and ready to chat and use commands...
            print(f'Logged in as | {self.nick}')
            print(f'User id is | {self.user_id}')

        async def event_message(self, message):
            # Messages with echo set to True are messages sent by the bot...
            # For now we just want to ignore them...
            if message.echo:
                return

            # Print the contents of our message to console...
            if message.author.name not in self.excluded_users_list:
                print(message)
                print(message.content)
                print(message.author.name, ": ", message.content)
                self.twitch_chat_fetch.add_to_chat_log(message.author.name, message.content)

            # Since we have commands and are overriding the default `event_message`
            # We must let the bot know we want to handle and invoke our commands...
            await self.handle_commands(message)

        @commands.command()
        async def hello(self, ctx: commands.Context):
            # Send a hello back!
            await ctx.send(f'Hello {ctx.author.name}!')