#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
from pathlib import Path

class Config(configparser.ConfigParser):
    def __init__(self):
        super().__init__(
            interpolation=configparser.ExtendedInterpolation()
        )

    def resolve(self, value: str, section="DEFAULT"):
        try:
            return self._interpolation.before_get(
                self,
                section,
                "__tmp__",
                value,
                self._unify_values(section, {})
            )
        except configparser.InterpolationError as e:
            print(f"Invalid config interpolation : \"{value}\" from section \"{section}\"")
            return None
    
    @staticmethod
    def DefaultDict() -> dict:
        return {
            "DEFAULT": {
                "root": "${cwd}/test",
                "logs": "${cwd}/logs",
            }
        }
    
class ConfigPath:
    def __init__(self, template: str):
        self.template = template

    def resolve(self, config: Config) -> Path:
        resolved = config.resolve(self.template)
        return Path(resolved)

    def __str__(self):
        return self.template