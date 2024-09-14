from queue import Queue
import threading
from pluginInterface import TranslationPluginInterface
import gradio as gr
from pluginSelectionBase import PluginSelectionBase
from liveTextbox import LiveTextbox
import LAV_utils


class Translate(PluginSelectionBase):
    input_queue = Queue()
    output_event_listeners = []
    input_process_thread = None
    log_live_textbox = LiveTextbox()
    queue_live_textbox = LiveTextbox()

    def __init__(self) -> None:
        super().__init__(TranslationPluginInterface)

    def create_ui(self):
        with gr.Tab("Translate"):
            super().create_plugin_selection_ui()
            # translation UI
            original_text_textbox = gr.Textbox(
                label="Original Text", lines=3, render=False)
            translated_text_textbox = gr.Textbox(
                label="Translated Text", lines=3, render=False)

            gr.Interface(
                fn=self.translate_wrapper,
                inputs=[original_text_textbox],
                outputs=[translated_text_textbox],
                allow_flagging="never",
                examples=["My name is Wolfgang and I live in Berlin",
                          "Have you ever kept goldfish as pets? They're very cute."]
            )
            with gr.Accordion("Console", open=False):
                self.log_live_textbox.create_ui()
                self.queue_live_textbox.create_ui(
                    lines=3, max_lines=3, label="Input waiting to be processed: ")
            super().create_plugin_ui()

    def translate_wrapper(self, text):
        self.log_live_textbox.print(f"Input: {text}")
        result = self.current_plugin.translate(text)
        self.log_live_textbox.print(f"Translation: {result}")
        self.send_output(result)
        return result

    def receive_input(self, text):
        self.input_queue.put(text)
        self.process_input_queue()

    def process_input_queue(self):
        def translate_text():
            while (not self.input_queue.empty()):
                self.translate_wrapper(self.input_queue.get())
                self.queue_live_textbox.set(
                    LAV_utils.queue_to_list(self.input_queue))

        # Check if the current thread is alive
        if self.input_process_thread is None or not self.input_process_thread.is_alive():
            # Create and start a new thread
            self.input_process_thread = threading.Thread(target=translate_text)
            self.input_process_thread.start()

    def send_output(self, output):
        print(f"translation output:{output}")
        for subcriber in self.output_event_listeners:
            subcriber(output)

    def add_output_event_listener(self, function):
        self.output_event_listeners.append(function)
