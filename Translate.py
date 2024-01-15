from pluginLoader import plugin_loader
from pluginInterface import TranslationPluginInterface
import gradio as gr
import utils

selected_provider = None


def create_ui():
    category_name = plugin_loader.interface_to_category[TranslationPluginInterface]
    ProviderList, ProviderMap = utils.pluginToNameMap(
        plugin_loader.plugins[category_name])
    default_provider_name = ProviderList[0] if ProviderList else None
    global selected_provider
    selected_provider = ProviderMap[default_provider_name]
    with gr.Tab("Translate"):
        gr.Dropdown(
            choices=ProviderList,
            value=default_provider_name,
            type="value",
            label="Translation provider: ",
            info="Select the translation provider",
            interactive=True)
    load_provider()


def load_provider():
    global selected_provider
    if issubclass(type(selected_provider), TranslationPluginInterface):
        selected_provider.init()
        print(selected_provider.translate("This is a test message."))
