#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from .Job import Job
from typing import  NewType
from .types import *

@dataclass
class Sequence:
    # Identification
    id: SequenceID = INVALID_SEQUENCE_ID
    name: str = ""

    # Content
    jobs: list[Job] = field(default_factory=list)
    start: Job = None
    end: Job = None

    previous: list[Sequence] = field(default_factory=list)
    next: list[Sequence] = field(default_factory=list)