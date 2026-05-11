#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser

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