import gradio as gr
import threading
import time


class LiveTextbox():
    def __init__(self) -> None:
        self.messages = []
        self.lock = threading.Lock()

    def create_ui(self, lines=10, max_lines=10, label=None):
        textbox = gr.Textbox(lines=lines, container=label != None, label=label,
                             show_label=True, interactive=True, autoscroll=True)
        gr.Interface(fn=self.message_generator, inputs=[],
                     outputs=[textbox], live=True, allow_flagging=False, submit_btn=gr.Button(visible=False), stop_btn=gr.Button(visible=False), clear_btn=gr.Button(visible=False))

    def print(self, new_message, append_to_last=False):
        with self.lock:
            if append_to_last and self.messages:
                self.messages[-1] += new_message
            else:
                self.messages.append(new_message)

    def set(self, new_message:str):
        with self.lock:
            self.messages = new_message

    def clear(self):
        self.messages.clear()

    # Generator function for the Gradio interface
    def message_generator(self):
        last_yielded = None
        while True:
            with self.lock:
                concatenated_messages = "\n".join(self.messages)
            if concatenated_messages != last_yielded:
                yield concatenated_messages
                last_yielded = concatenated_messages
            time.sleep(0.1)  # Short sleep to prevent tight loop
