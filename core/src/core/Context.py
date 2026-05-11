#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Context:
    values:dict[str, Any] = field(default_factory=dict)