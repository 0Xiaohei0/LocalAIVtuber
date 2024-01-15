import subprocess
from pluginInterface import TTSPluginInterface
import os


class VoiceVox(TTSPluginInterface):
    voicevox_server_started = False

    def init(self):
        print("initializing voicevox...")
        self.start_voicevox_server()

    def synthesize(self, text):
        raise NotImplementedError

    def start_voicevox_server(self):
        if (self.voicevox_server_started):
            return
        # start voicevox server
        current_module_directory = os.path.dirname(__file__)
        executable_path = os.path.join(
            current_module_directory, "VoicevoxEngine", "run.exe")
        # Run the executable
        subprocess.Popen(executable_path)
        self.voicevox_server_started = True
