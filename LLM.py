import inspect
from queue import Queue
import threading
from pluginInterface import LLMPluginInterface
import gradio as gr
from pluginSelectionBase import PluginSelectionBase
import os
from liveTextbox import LiveTextbox
import LAV_utils


class LLM(PluginSelectionBase):
    history = []
    input_queue = Queue()
    input_process_thread = None
    system_prompt_text = ""
    liveTextbox = LiveTextbox()
    process_queue_live_textbox = LiveTextbox()
    
    remember_history = True

    def __init__(self) -> None:
        super().__init__(LLMPluginInterface)

        self.output_event_listeners = []
        self.full_output_event_listeners = []
        self.context_file_path = "Context.txt"
        self.LLM_output = ""
        
        self.history = []
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
                
                self.reset_button = gr.Button("reset chat history")
                self.reset_button.click(fn=self.reset_chat, inputs=[], outputs=[])
                with gr.Accordion("Console"):
                    self.liveTextbox.create_ui()
                    self.process_queue_live_textbox.create_ui(
                        lines=3, max_lines=3, label="Input waiting to be processed: ")
            super().create_plugin_ui()

    def reset_chat(self):
        self.history.clear()
        
    def is_generator(self): return inspect.isgeneratorfunction(
        self.current_plugin.predict)

    def predict_wrapper(self, message, history, system_prompt):
        print(f"history: {history}")
        # determine if predict function is generator and sends output to other modules
        
        self.start_of_response = True
        self.liveTextbox.print(f"Input: {message}")
        result = self.current_plugin.predict(message, history, system_prompt)
        self.liveTextbox.print(f"AI: ")
        if self.is_generator():
            processed_idx = 0
            for output in result:
                self.LLM_output = output
                if self.is_sentence_end(self.LLM_output):
                    self.send_output(self.LLM_output[processed_idx:])
                    self.liveTextbox.print(
                        self.LLM_output[processed_idx:], append_to_last=True)
                    processed_idx = len(self.LLM_output)
                yield output
            if not processed_idx == len(self.LLM_output):
                # send any remaining output
                self.send_output(self.LLM_output[processed_idx:])
                self.liveTextbox.print(
                    self.LLM_output[processed_idx:], append_to_last=True)
        else:
            self.LLM_output = result
            self.send_output(result)
            self.liveTextbox.print(result, append_to_last=True)
            return result
        self.send_full_output(self.LLM_output)
        if self.remember_history:
            self.history.append([message, self.LLM_output])

    def load_content(self):
        with open(self.context_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            self.system_prompt_text = content
            return content

    def update_file(self, new_content):
        self.context = new_content
        with open(self.context_file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        self.system_prompt_text = new_content

    def send_output(self, output):
        for subcriber in self.output_event_listeners:
            subcriber(output)
    
    def send_full_output(self, output):
        for subcriber in self.full_output_event_listeners:
            subcriber(output)

    def receive_input(self, text):
        self.input_queue.put(text)
        self.process_input_queue()

    def add_output_event_listener(self, function, full_response = False):
        if full_response:
            self.full_output_event_listeners.append(function)
        else:
            self.output_event_listeners.append(function)

    # Check if the last character of the word is a sentence-ending punctuation for the given language
    def is_sentence_end(self, word):
        sentence_end_punctuation = {'.', '?', '!', '。', '？', '！','\n'}
        if len(word) > 0:
            return word[-1] in sentence_end_punctuation
        else: return True

    def process_input_queue(self):
        # Check if the current thread is alive
        if self.input_process_thread is None or not self.input_process_thread.is_alive():
            # Create and start a new thread
            self.input_process_thread = threading.Thread(
                target=self.generate_response)
            self.input_process_thread.start()

    def generate_response(self):
        while (not self.input_queue.empty()):
            next_input = self.input_queue.get()
            response = self.predict_wrapper(
                next_input, self.history, self.system_prompt_text)
            if self.is_generator():
                for _ in response:
                    pass  # need to keep iterating the generator
                    self.process_queue_live_textbox.set(
                        LAV_utils.queue_to_list(self.input_queue))
