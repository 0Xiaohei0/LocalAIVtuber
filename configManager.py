import configparser
import os

class ConfigManager:
    def __init__(self, config_file="config.ini"):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        
        # Load the config file if it exists
        if os.path.exists(config_file):
            self.config.read(config_file)

    def save_config(self, section, key, value):
        """Save a configuration value under a section (group)."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, value)
        
        # Write the updated configuration to the file
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def load_config(self, section, key):
        """Load a configuration value from a section."""
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        else:
            return ""

    def load_section(self, section):
        """Load all key-value pairs from a section (group)."""
        if self.config.has_section(section):
            return dict(self.config.items(section))
        else:
            return {}

config_manager = ConfigManager()