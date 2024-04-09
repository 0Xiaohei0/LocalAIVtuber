class InputPluginInterface:
    input_event_listeners = []

    def init(self):
        pass

    def create_ui(self):
        pass

    # call this function to send your gathered input to next component
    def process_input(self, input: str):
        for listener in self.input_event_listeners:
            listener(input)


class LLMPluginInterface:
    def init(self):
        pass

    def predict(self, message, history):
        raise NotImplementedError

    def create_ui(self):
        pass


class TranslationPluginInterface:
    def init(self):
        pass

    def translate(self, text):
        raise NotImplementedError

    # Use the two letter language codes from here: https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
    def get_input_language_code(self):
        raise NotImplementedError

    def get_output_language_code(self):
        raise NotImplementedError

    def create_ui(self):
        pass


class TTSPluginInterface:
    def init(self):
        pass

    def synthesize(self, text):
        raise NotImplementedError

    def create_ui(self):
        pass


class VtuberPluginInterface:
    class AvatarData():
        mouth_open = 0
        # TODO current emotion, current pheonome etc

    avatar_data = AvatarData()

    def init(self):
        pass

    def create_ui(self):
        pass

    def set_avatar_data(self, data):
        self.avatar_data = data
