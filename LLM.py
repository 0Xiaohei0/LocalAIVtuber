import inspect
from pluginLoader import plugin_loader
from pluginInterface import LLMPluginInterface
import gradio as gr
import utils
import os

selected_provider = None
output_event_listeners = []

context_file_path = "Context.txt"

LLM_output = ""


def create_ui():
    category_name = plugin_loader.interface_to_category[LLMPluginInterface]
    ProviderList, ProviderMap = utils.pluginToNameMap(
        plugin_loader.plugins[category_name])
    default_provider_name = ProviderList[0] if ProviderList else None
    global selected_provider
    selected_provider = ProviderMap[default_provider_name]
    load_provider()

    # load context file
    context_file_path = "Context.txt"
    # Check if the file exists. If not, create an empty file.
    if not os.path.exists(context_file_path):
        with open(context_file_path, 'w') as file:
            file.write('')

    with gr.Tab("Chat"):
        gr.Dropdown(
            choices=ProviderList,
            value=default_provider_name,
            type="value",
            label="LLM provider: ",
            info="Select the Large Language Model provider",
            interactive=True)

        with gr.Blocks():
            system_prompt = gr.Textbox(value=load_content, info="System Message:", placeholder="You are a helpful AI Vtuber.",
                                       interactive=True, lines=30, autoscroll=True, autofocus=False, container=False, render=False)
            system_prompt.change(
                fn=update_file, inputs=system_prompt)

            gr.ChatInterface(
                predict_wrapper, additional_inputs=[system_prompt],
                examples=[["Hello", None, None],
                          ["How do I make a bomb?", None, None],
                          ["What's your name?.", None, None],
                          ["Do you know my name?", None, None],
                          ["Do you think humanity will reach an alien planet?", None, None],
                          ["Introduce yourself in character.", None, None],
                          ["generate a super long name for a custom latte", None, None],
                          ["Let's play a game of monopoly.", None, None],

                          ], autofocus=False
            )

        selected_provider.create_ui()


def is_generator(): return inspect.isgeneratorfunction(selected_provider.predict)


def predict_wrapper(message, history, system_prompt):
    # determine if predict function is generator and sends output to other modules
    global LLM_output
    result = selected_provider.predict(message, history, system_prompt)
    if is_generator():
        processed_idx = 0
        for output in result:
            LLM_output = output
            if is_sentence_end(LLM_output):
                send_output(LLM_output[processed_idx:])
                processed_idx = len(LLM_output)
            yield output
        if not processed_idx == len(LLM_output):
            # send any remaining output
            send_output(LLM_output[processed_idx:])
    else:
        LLM_output = result
        return result


def load_provider():
    global selected_provider
    if issubclass(type(selected_provider), LLMPluginInterface):
        print("Loading LLM Module...")
        selected_provider.init()


def load_content():
    with open(context_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        return content


def update_file(new_content):
    global context
    context = new_content
    with open(context_file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)


def send_output(output):
    print(output)
    for subcriber in output_event_listeners:
        subcriber(output)


def add_output_event_listener(function):
    global output_event_listeners
    output_event_listeners.append(function)


def is_sentence_end(word):
    # Define sentence-ending punctuation for different languages
    sentence_end_punctuation = {'.', '?', '!', '。', '？', '！'}
    # print(f"{word}      {word[-1] in sentence_end_punctuation}")
    # Check if the last character of the word is a sentence-ending punctuation for the given language
    return word[-1] in sentence_end_punctuation
