import os
import yaml

class ConfigLoader:
    """
    Load YAML config files and provide dynamic access to config sections.
    Always load fresh config to ensure real-time updates.
    """
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self._configs = {}

    def load(self, name):
        """Load a YAML config file from the config_dir."""
        path = os.path.join(self.config_dir, f"{name}.yaml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        self._configs[name] = config
        return config

    def get(self, name, section=None, reload=False):
        """
        Get config by name (file name, without .yaml).
        Optionally get a section.
        Set reload=True to force reload from disk.
        """
        if reload or name not in self._configs:
            self.load(name)
        if section:
            return self._configs[name].get(section, {})
        return self._configs[name]

    def refresh_all(self):
        """Reload all configs from disk."""
        for name in list(self._configs.keys()):
            self.load(name)

# Usage example
if __name__ == "__main__":
    loader = ConfigLoader()
    strategy = loader.get("strategy", reload=True)
    print(strategy)
