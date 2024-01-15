import subprocess
from pluginInterface import TTSPluginInterface


class VoiceVoxPlugin(TTSPluginInterface):
    voicevox_server_started = False

    def init(self):
        self.start_voicevox_server()

    def synthesize(self, text):
        raise NotImplementedError

    def start_voicevox_server(self):
        if (self.voicevox_server_started):
            return
        # start voicevox server
        subprocess.Popen("VOICEVOX\\run.exe")
        self.voicevox_server_started = True
