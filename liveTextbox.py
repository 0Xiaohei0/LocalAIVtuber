import gradio as gr
import threading
import time


class LiveTextbox():
    # Shared list to hold messages
    messages = []

    # Lock for thread-safe operations on `messages`
    lock = threading.Lock()

    def create_ui(self):
        textbox = gr.Textbox(lines=10, max_lines=10,
                             label="Console log:", show_label=True, interactive=False)
        gr.Interface(fn=self.message_generator, inputs=None,
                     outputs=[textbox], live=True, allow_flagging=False)

    def print(self, new_message):
        with self.lock:
            self.messages.append(new_message)

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
