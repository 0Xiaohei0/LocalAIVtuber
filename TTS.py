from pluginLoader import plugin_loader
from pluginInterface import TTSPluginInterface
import gradio as gr


def create_ui():
    category_name = plugin_loader.interface_to_category[TTSPluginInterface]
    TTSProviderList = []
    for tts_provider in plugin_loader.plugins[category_name]:
        TTSProviderList.append(tts_provider.__class__.__name__)
    default_provider = TTSProviderList[0] if TTSProviderList else None
    with gr.Tab("TTS"):
        Input_selection = gr.Dropdown(
            choices=TTSProviderList,
            value=default_provider,
            type="value",
            label="TTS provider: ",
            info="Select the text to speech provider",
            interactive=True)
