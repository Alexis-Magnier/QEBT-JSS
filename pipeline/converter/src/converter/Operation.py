#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any
from enum import Enum

class Resource(Enum):
    NONE = 0
    HUMAN = 1
    ROBOT = 2
    COLLABORATIVE = 3

    @staticmethod
    def From_str(data:str) -> Operation:
        match data.lower():
            case "h": return Resource.HUMAN
            case "r": return Resource.ROBOT
            case "co": return Resource.COLLABORATIVE
        raise ValueError(f"Unknown resource type : {data}")
    
    def to_str(self) -> str:
        match self:
            case Resource.HUMAN: return "H"
            case Resource.ROBOT: return "R"
            case Resource.COLLABORATIVE: return "Co"

# the frozen parameters makes the class immutable after initialisation.
# Usefull for hashing for dictionnaries
@dataclass(frozen=True)
class Operation:
    job: Any
    operation: Any
    resource: Resource

    @staticmethod
    def From_string(data:str) -> Operation:
        job, operation, resource = data.split(',')
        return Operation(
            job = job,
            operation = operation,
            resource = Resource(resource)
        )

    def to_string(self) -> Operation:
        return f"{self.job},{self.operation},{self.resource.to_str()}"

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