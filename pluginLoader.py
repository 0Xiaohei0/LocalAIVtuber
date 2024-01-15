import importlib
import os
from pluginInterface import *

plugin_directory = "plugins"


class PluginLoader:
    def __init__(self, plugin_directory):
        self.plugin_directory = plugin_directory
        self.interface_to_category = {
            InputPluginInterface: 'input_gathering',
            LLMPluginInterface: 'input_processing',
            TTSPluginInterface: 'output_generation'
        }
        self.plugins = {category: []
                        for category in self.interface_to_category.values()}

    def load_plugins(self):
        for filename in os.listdir(self.plugin_directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                module = importlib.import_module(
                    f"{self.plugin_directory}.{module_name}")
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if isinstance(attribute, type):
                        # Exclude based on naming convention
                        if attribute_name.endswith('Interface'):
                            continue
                        for interface, category in self.interface_to_category.items():
                            if issubclass(attribute, interface):
                                self.plugins[category].append(attribute())
                                break  # Assumes one plugin class implements only one interface


plugin_loader = PluginLoader(plugin_directory)
