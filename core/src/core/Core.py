#!/usr/bin/env python
# -*- coding: utf-8 -*-

import semver
from typing import ClassVar
from dataclasses import dataclass, field

from .Policy import *
from .Config import Config

@dataclass
class Core:
    VERSION: ClassVar[semver.Version] = semver.Version(0, 1, 0)
    name: str = ""
    config: Config = None
    QTable: PolicyTable = field(default_factory=PolicyTable)