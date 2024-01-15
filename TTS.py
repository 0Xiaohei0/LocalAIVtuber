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
        gr.Interface(
            fn=selected_provider.synthesize,
            inputs=[gr.Textbox(label="Original Text")],
            outputs=[gr.Audio(label="Synthesized Voice")],
            allow_flagging="never",
            examples=["すぅ…はぁ——おはようさん、朝の空気は清々しくて気持ちええなぁ、深呼吸して頭もすっきりや。",
                      "金魚飼ったことある？大人しゅうて、めっちゃ可愛ええんや。",
                      "全身ポカポカで気持ちええわぁ～、浮いとるみたい。"]
        )
    load_provider()


def load_provider():
    global selected_provider
    if issubclass(type(selected_provider), TTSPluginInterface):
        print("Loading TTS Module...")
        selected_provider.init()
