from pluginLoader import plugin_loader
from pluginInterface import TTSPluginInterface

category_name = plugin_loader.interface_to_category[TTSPluginInterface]
for ttsProvider in plugin_loader.plugins[category_name]:
    # populate dropdown with plugin name
