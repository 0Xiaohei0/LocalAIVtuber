
from pluginInterface import TranslationPluginInterface
from transformers import MarianMTModel, MarianTokenizer
import os
import pysbd


class LocalENToJA(TranslationPluginInterface):
    def init(self):
        # current_module_directory = os.path.dirname(__file__)
        # model_path = os.path.join(
        #     current_module_directory, "models--staka--fugumt-en-ja", "snapshots", "2d6da1c7352386e12ddd46ce3d0bbb2310200fcc")
        # self.fugu_translator = pipeline(
        #     'translation', model=model_path)
        model_name = "Helsinki-NLP/opus-tatoeba-en-ja"
        self.model = MarianMTModel.from_pretrained(model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)

    def translate(self, text):
        seg_en = pysbd.Segmenter(language="en", clean=False)
        segmented_text = seg_en.segment(text)
        data = self.generate(segmented_text, self.model, self.tokenizer)
        print(f"LocalENToJA output:{data}")
        concatenated_text = '。'.join(data)
        processed_output = self.preprocess_input(concatenated_text)
        return processed_output

    def generate(self, text, model, tokenizer):
        # Tokenize the input text
        inputs = tokenizer(text, return_tensors="pt", padding=True)

        translated = model.generate(**inputs, num_beams=5, max_new_tokens=50)

        # Decode the generated tokens
        return [tokenizer.decode(t, skip_special_tokens=True) for t in translated]

    def get_input_language_code(self):
        return 'en'

    def get_output_language_code(self):
        return 'ja'

    def preprocess_input(self, text):
        text = text.replace(" ", "")
        return text
