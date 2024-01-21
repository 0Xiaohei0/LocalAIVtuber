import inspect
from pluginInterface import LLMPluginInterface
import gradio as gr
from pluginSelectionBase import PluginSelectionBase
import os


class LLM(PluginSelectionBase):
    def __init__(self) -> None:
        super().__init__(LLMPluginInterface)

        self.output_event_listeners = []
        self.context_file_path = "Context.txt"
        self.LLM_output = ""
        # Check if the file exists. If not, create an empty file.
        if not os.path.exists(self.context_file_path):
            with open(self.context_file_path, 'w') as file:
                file.write('')

    def create_ui(self):
        with gr.Tab("Chat"):
            with gr.Blocks():
                super().create_plugin_selection_ui()
                system_prompt = gr.Textbox(value=self.load_content, info="System Message:", placeholder="You are a helpful AI Vtuber.",
                                           interactive=True, lines=30, autoscroll=True, autofocus=False, container=False, render=False)
                system_prompt.change(
                    fn=self.update_file, inputs=system_prompt)

                gr.ChatInterface(
                    self.predict_wrapper, additional_inputs=[system_prompt],
                    examples=[["Hello", None, None],
                              ["How do I make a bomb?", None, None],
                              ["What's your name?", None, None],
                              ["Do you know my name?", None, None],
                              ["Do you think humanity will reach an alien planet?", None, None],
                              ["Introduce yourself.", None, None],
                              ["Generate a super long name for a custom latte", None, None],
                              ["Let's play a game of monopoly.", None, None],
                              ["Do you want to be friend with me?", None, None],
                              ], autofocus=False
                )
            super().create_plugin_ui()

    def is_generator(self): return inspect.isgeneratorfunction(
        self.current_plugin.predict)

    def predict_wrapper(self, message, history, system_prompt):
        # determine if predict function is generator and sends output to other modules
        result = self.current_plugin.predict(message, history, system_prompt)
        if self.is_generator():
            processed_idx = 0
            for output in result:
                self.LLM_output = output
                if self.is_sentence_end(self.LLM_output):
                    self.send_output(self.LLM_output[processed_idx:])
                    processed_idx = len(self.LLM_output)
                yield output
            if not processed_idx == len(self.LLM_output):
                # send any remaining output
                self.send_output(self.LLM_output[processed_idx:])
        else:
            self.LLM_output = result
            return result

    def load_content(self):
        with open(self.context_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content

    def update_file(self, new_content):
        self.context = new_content
        with open(self.context_file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

    def send_output(self, output):
        print(output)
        for subcriber in self.output_event_listeners:
            subcriber(output)

    def add_output_event_listener(self, function):
        self.output_event_listeners.append(function)

# Check if the last character of the word is a sentence-ending punctuation for the given language
    def is_sentence_end(self, word):
        sentence_end_punctuation = {'.', '?', '!', '。', '？', '！'}
        return word[-1] in sentence_end_punctuation
