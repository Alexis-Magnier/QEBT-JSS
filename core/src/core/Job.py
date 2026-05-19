#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from .Task import Task
from .types import *

TASKS_NODE = "tasks"
NAME_ENTRY = "name"
REQUIRMENTS_ENTRY = "requires"
PROBABILITY_ENTRY = "probability"

@dataclass
class Job:
    # Serialisable data
    id: JobID = INVALID_JOB_ID
    name: str = ""
    probability: float = 1.0
    requirments: list[JobID] = field(default_factory=list)

    # runtime
    next: list[Job] = field(default_factory=list)
    previous: list[Job] = field(init=False, default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    sequence = None
    
    
    @staticmethod
    def From_dict(id:int, data: dict) -> Job:
        """ Creates a job from a dictionary
        """

        tasks = [
            Task.From_dict(j)
            for j in data.get(TASKS_NODE, [])
        ]

        return Job(
            id=id,
            name=data.get(NAME_ENTRY, ""),
            requirments=data.get(REQUIRMENTS_ENTRY, []),
            probability=data.get(PROBABILITY_ENTRY, 1.0),
            tasks=tasks,
        )

    def __hash__(self):
        return self.id