
from pluginInterface import TranslationPluginInterface
from transformers import pipeline
import os
import pysbd


class LocalENToJA(TranslationPluginInterface):
    def init(self):
        # current_module_directory = os.path.dirname(__file__)
        # model_path = os.path.join(
        #     current_module_directory, "models--staka--fugumt-en-ja", "snapshots", "2d6da1c7352386e12ddd46ce3d0bbb2310200fcc")
        # self.fugu_translator = pipeline(
        #     'translation', model=model_path)
        self.fugu_translator = pipeline(
            "translation", model="Helsinki-NLP/opus-tatoeba-en-ja")

    def translate(self, text):
        seg_en = pysbd.Segmenter(language="en", clean=False)
        segmented_text = seg_en.segment(text)
        data = self.fugu_translator(segmented_text)
        concatenated_text = ''.join(
            item['translation_text'] for item in data)
        return concatenated_text

    def get_input_language_code(self):
        return 'en'

    def get_output_language_code(self):
        return 'ja'
