from pluginLoader import plugin_loader
from pluginInterface import TTSPluginInterface
import gradio as gr
import utils

selected_provider = None


def create_ui():
    category_name = plugin_loader.interface_to_category[TTSPluginInterface]
    TTSProviderList, TTSProviderMap = utils.pluginToNameMap(
        plugin_loader.plugins[category_name])
    default_provider_name = TTSProviderList[0] if TTSProviderList else None
    global selected_provider
    selected_provider = TTSProviderMap[default_provider_name]
    with gr.Tab("TTS"):
        gr.Dropdown(
            choices=TTSProviderList,
            value=default_provider_name,
            type="value",
            label="TTS provider: ",
            info="Select the text to speech provider",
            interactive=True)
    print("loading provider...")
    load_provider()


def load_provider():
    global selected_provider
    if issubclass(type(selected_provider), TTSPluginInterface):
        selected_provider.init()
