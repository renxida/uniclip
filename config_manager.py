import json
import os

class ConfigManager:
    def __init__(self, config_path='~/.uniclip'):
        self.config_path = os.path.expanduser(config_path)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
