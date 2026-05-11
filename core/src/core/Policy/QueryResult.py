#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from . import Policy

@dataclass
class QueryResult:
    result: list[tuple[Policy, float]] = field(default_factory=list)
    