from threading import Thread
import time
import traceback
from twitchio.ext import commands
from pluginInterface import InputPluginInterface


class TwitchChatFetch(InputPluginInterface):
    twitchbot = None
    read_chat_twitch_thread = None
    read_chat_twitch_thread_running = False

    twitch_access_token = ''
    twitch_channel_name = ''

    def init(self):
        pass

    def gather_input(self):
        raise NotImplementedError

    def create_ui(self):
        pass

    def read_chat_twitch(self):
        print("startinging chat fetching...")
        global twitchbot
        global read_chat_twitch_thread_running, read_chat_twitch_thread
        global twitch_access_token, twitch_channel_name
        twitchbot = Bot(twitch_access_token, [twitch_channel_name])
        read_chat_twitch_thread = Thread(target=self.runbot)
        read_chat_twitch_thread.start()
        read_chat_twitch_thread_running = True

    def runbot(self):
        print("Chat fetching started")
        twitchbot.run()

    def stop_read_chat_twitch(self):
        print("Twitch fetching can only be stopped by closing the program.")


class Bot(commands.Bot):

    def __init__(self, token, initial_channels):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=token,
                         prefix='?', initial_channels=initial_channels)
        global excluded_users_list
        # Function to reload the excluded users from the file
        reload_thread = Thread(target=self.reload_excluded_users)
        reload_thread.start()

    def reload_excluded_users(self):
        while True:
            try:
                global excluded_users_list
                file_path = "excluded_users.txt"
                with open(file_path, "r") as file:
                    content = file.read()
                    excluded_users_list = content.split("\n")
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
        if message.author.name not in excluded_users_list:
            print(message)
            print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')
