#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any

# the frozen parameters makes the class immutable after initialisation.
# Usefull for hashing for dictionnaries
@dataclass(frozen=True)
class Operation:
    job: Any
    operation: Any
    resource: Any

@dataclass
class OperationData:
    start_time: float = 0
    end_time: float = 0
    active: bool = False

    def duration(self) -> float:
        return self.end_time - self.start_time 