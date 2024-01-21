from pluginInterface import TranslationPluginInterface


class NoTranslate(TranslationPluginInterface):
    def translate(self, text):
        return text

    def get_input_language_code(self):
        return 'any'

    def get_output_language_code(self):
        return 'any'
