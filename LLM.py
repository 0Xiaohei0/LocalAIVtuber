from pluginLoader import plugin_loader
from pluginInterface import LLMPluginInterface
import gradio as gr
import utils

selected_provider = None


def create_ui():
    category_name = plugin_loader.interface_to_category[LLMPluginInterface]
    ProviderList, ProviderMap = utils.pluginToNameMap(
        plugin_loader.plugins[category_name])
    default_provider_name = ProviderList[0] if ProviderList else None
    global selected_provider
    selected_provider = ProviderMap[default_provider_name]
    load_provider()
    with gr.Tab("Chat"):
        gr.Dropdown(
            choices=ProviderList,
            value=default_provider_name,
            type="value",
            label="LLM provider: ",
            info="Select the Large Language Model provider",
            interactive=True)

        selected_provider.create_ui()


def load_provider():
    global selected_provider
    if issubclass(type(selected_provider), LLMPluginInterface):
        print("Loading LLM Module...")
        selected_provider.init()
