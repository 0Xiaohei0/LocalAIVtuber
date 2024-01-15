class InputPluginInterface:
    def init(self):
        pass

    def gather_input(self):
        raise NotImplementedError


class LLMPluginInterface:
    def init(self):
        pass

    def predict(self, message, history):
        raise NotImplementedError


class TTSPluginInterface:
    def init(self):
        pass

    def synthesize(self, text):
        raise NotImplementedError
