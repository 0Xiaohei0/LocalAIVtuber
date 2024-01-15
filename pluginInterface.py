class InputPluginInterface:
    def init(self):
        raise NotImplementedError

    def gather_input(self):
        raise NotImplementedError


class LLMPluginInterface:
    def init(self):
        raise NotImplementedError

    def predict(self, message, history):
        raise NotImplementedError


class TTSPluginInterface:
    def init(self):
        raise NotImplementedError

    def synthesize(self, text):
        raise NotImplementedError
