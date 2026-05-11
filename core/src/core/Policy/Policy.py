#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from ..types import *

@dataclass
class Policy:
    id: PolicyID = INVALID_POLICY_ID
    name: str = ""

    domains: set[str] = field(default_factory=set)
    descriptors: dict[str] = field(default_factory=dict)
    parameters: list[str] = field(default_factory=list)
    implementation: int = 0 # The actual behaviour tree

    @staticmethod
    def From_dict(data:dict) -> Policy:
        return Policy(
            id = data["id"],
            name = data.get("name", ""),
            domains = set(data.get("domains", [])),
            descriptors = data.get("descriptors", {}),
            parameters = data.get("parameters", {}),
            implementation = data.get("implementation", None)
        )