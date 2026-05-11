#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from .types import *

@dataclass
class Query:
    domains: set[str] = field(default_factory=set)
    parameters: list = field(default_factory=list)
    descriptors: dict = field(default_factory=dict)
    similarity: dict = field(default_factory=dict)

    @staticmethod
    def From_dict(data:dict) -> Query:
        return Query(
            domains = set(data.get("domains", [])),
            parameters = data.get("parameters", ""),
            descriptors = data.get("descriptors", ""),
            similarity = data.get("similarity", ""),
        )