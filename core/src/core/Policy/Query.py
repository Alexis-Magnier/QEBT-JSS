#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from .types import *

@dataclass
class Query:
    domains: set[str] = field(default_factory=set)
    parameters: dict = field(default_factory=dict())
    descriptors: dict = field(default_factory=dict)
    weights: dict = field(default_factory=dict)

    @staticmethod
    def From_dict(data:dict) -> Query:
        return Query(
            domains = set(data.get("domains", [])),
            parameters = data.get("parameters", dict()),
            descriptors = data.get("descriptors", dict()),
            weights = data.get("weights", dict()),
        )