from pathlib import Path
from .Config import Config

class ConfigPath:
    def __init__(self, template: str):
        self.template = template

    def resolve(self, config: Config) -> Path:
        resolved = config.resolve(self.template)
        return Path(resolved)

    def __str__(self):
        return self.template