#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any
import core

# the frozen parameters makes the class immutable after initialisation.
# Usefull for hashing for dictionnaries
@dataclass(frozen=True)
class Operation:
    job: Any
    operation: Any
    resource: core.Resource

    @staticmethod
    def From_string(data:str, resourceRegistry:core.ResourceRegistry) -> Operation:
        job, operation, resource = data.split(',')
        return Operation(
            job = job,
            operation = operation,
            resource = resourceRegistry.resources[int(resource)]
        )

    def to_string(self) -> Operation:
        return f"{self.job},{self.operation},{self.resource.id}"

@dataclass
class OperationData:
    start_time: float = 0
    end_time: float = 0
    active: bool = False

    def duration(self) -> float:
        return self.end_time - self.start_time 
    
    @staticmethod
    def From_dict(data:dict) -> OperationData:
        return OperationData(
            start_time = data["start_time"],
            end_time = float(data["end_time"]),
            active = bool(data["active"])
        )

    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "active": self.active
        }