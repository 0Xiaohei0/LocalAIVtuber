from queue import Queue
import threading
from pluginLoader import plugin_loader
from pluginInterface import TranslationPluginInterface
import gradio as gr
import utils

selected_provider = None
input_queue = Queue()
output_event_listeners = []
input_process_thread = None


def create_ui():
    category_name = plugin_loader.interface_to_category[TranslationPluginInterface]
    ProviderList, ProviderMap = utils.pluginToNameMap(
        plugin_loader.plugins[category_name])
    default_provider_name = ProviderList[0] if ProviderList else None
    global selected_provider
    selected_provider = ProviderMap[default_provider_name]
    load_provider()
    with gr.Tab("Translate"):
        # translation provider selection
        gr.Dropdown(
            choices=ProviderList,
            value=default_provider_name,
            type="value",
            label="Translation provider: ",
            info="Select the translation provider",
            interactive=True)
        # translation UI
        original_text_textbox = gr.Textbox(
            label="Original Text", lines=3, render=False)
        translated_text_textbox = gr.Textbox(
            label="Translated Text", lines=3, render=False)

        gr.Interface(
            fn=translate_wrapper,
            inputs=[original_text_textbox],
            outputs=[translated_text_textbox],
            allow_flagging="never",
            examples=["My name is Wolfgang and I live in Berlin",
                      "VHave you ever kept goldfish as pets? They're very cute."]
        )


def load_provider():
    global selected_provider
    if issubclass(type(selected_provider), TranslationPluginInterface):
        print("Loading Translation Module...")
        selected_provider.init()


def translate_wrapper(text):
    result = selected_provider.translate(text)
    send_output(result)
    return result


def receive_input(text):
    input_queue.put(text)
    process_input_queue()


def process_input_queue():
    def translate_text():
        while (not input_queue.empty()):
            translate_wrapper(input_queue.get())

    global input_process_thread
    # Check if the current thread is alive
    if input_process_thread is None or not input_process_thread.is_alive():
        # Create and start a new thread
        input_process_thread = threading.Thread(target=translate_text)
        input_process_thread.start()


def send_output(output):
    print(output)
    for subcriber in output_event_listeners:
        subcriber(output)


def add_output_event_listener(function):
    global output_event_listeners
    output_event_listeners.append(function)
