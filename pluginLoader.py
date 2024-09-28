import importlib.util
import json
import os
import subprocess
from pluginInterface import *

plugin_directory = "plugins"
temp_ignore = [] #["silero", "Local_LLM", "voicevox"]

class PluginLoader:
    def __init__(self, plugin_directory):
        self.current_module_directory = os.path.dirname(__file__)
        self.plugin_directory = os.path.join(self.current_module_directory,plugin_directory) 
        self.interface_to_category = {
            InputPluginInterface: 'input_gathering',
            LLMPluginInterface: 'language_model',
            TranslationPluginInterface: 'translation',
            TTSPluginInterface: 'text_to_speech',
            VtuberPluginInterface: 'vtuber'
        }
        self.plugins = {category: []
                        for category in self.interface_to_category.values()}
        
        self.plugin_setting_path = os.path.join(self.current_module_directory, "modules.json")
        self.plugin_setting= {}

    def load_plugins(self):
        # First, load plugins directly in the plugin_directory
        self._load_plugins_from_directory(self.plugin_directory)

        # Next, load plugins from subdirectories
        for item_name in os.listdir(self.plugin_directory):
            item_path = os.path.join(self.plugin_directory, item_name)
            
            # Check if the item is a directory
            if os.path.isdir(item_path):
                print(f"checking: {item_path}")
                #print(f"temp_ignore: {temp_ignore}")
                if item_name in temp_ignore: 
                    print(f"ignoring {item_path}")
                    continue

                # Check for requirements.txt in the plugin directory
                requirements_path = os.path.join(item_path, 'requirements.txt')
                if os.path.exists(requirements_path):
                    print(f"Installing requirements for plugin {item_path}")
                    subprocess.run(
                        ['pip', 'install', '-r', requirements_path], check=True)

                self._load_plugins_from_directory(item_path)
        
        if not os.path.exists(self.plugin_setting_path):
            with open(self.plugin_setting_path, "w") as json_file:
                json.dump(self.plugin_setting, json_file, indent=4)
            

    def _load_plugins_from_directory(self, directory):
        for file in os.listdir(directory):
            if file.endswith('.py') and not file.startswith('_'):
                module_path = os.path.join(directory, file)
                module_name = module_path.replace(os.sep, '.').rstrip('.py')
                # Remove plugin_directory from path
                module_name = module_name[len(self.plugin_directory) + 1:]
                plugin_name = os.path.basename(directory)

                # skip module loading based on config file
                if os.path.exists(self.plugin_setting_path):
                    with open(self.plugin_setting_path, "r") as json_file:
                        plugin_setting = json.load(json_file)
                    if plugin_setting[plugin_name] == False:
                        continue

                spec = importlib.util.spec_from_file_location(
                    module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if isinstance(attribute, type):
                        # Exclude based on naming convention
                        if attribute_name.endswith('Interface'):
                            continue
                        for interface, category in self.interface_to_category.items():
                            if issubclass(attribute, interface):
                                self.plugins[category].append(
                                    attribute())
                                self.plugin_setting[plugin_name] = True
                                break  # Assumes one plugin class implements only one interface


plugin_loader = PluginLoader(plugin_directory)
