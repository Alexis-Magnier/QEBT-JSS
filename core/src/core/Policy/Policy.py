#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from ..types import *

NAME_ENTRY = "name"
DOMAINS_ENTRY = "domains"
DESCRIPTORS_ENTRY = "descriptors"
PARAMETERS_ENTRY = "parameters"
IMPLMENTATION_ENTRY = "implementation"

@dataclass
class Policy:
    id: PolicyID = INVALID_POLICY_ID
    name: str = ""

    domains: set[str] = field(default_factory=set)
    descriptors: dict[str] = field(default_factory=dict)
    parameters: list[str] = field(default_factory=list)
    implementation: int = 0 # The actual behaviour tree

    @staticmethod
    def From_dict(id, data:dict) -> Policy:
        return Policy(
            id = id,
            name = data.get(NAME_ENTRY, ""),
            domains = set(data.get(DOMAINS_ENTRY, [])),
            descriptors = data.get(DESCRIPTORS_ENTRY, {}),
            parameters = data.get(PARAMETERS_ENTRY, {}),
            implementation = data.get(IMPLMENTATION_ENTRY, None)
        )