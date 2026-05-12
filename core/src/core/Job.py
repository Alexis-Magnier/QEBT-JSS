#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from .Task import Task
from .types import *

@dataclass(eq=False)
class Job:
    # Serialisable data
    id: JobID = INVALID_JOB_ID
    name: str = ""
    requirments: list[JobID] = field(default_factory=list)

    # runtime
    next: list[Job] = field(default_factory=list)
    previous: list[Job] = field(init=False, default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    sequence = None
    
    
    @staticmethod
    def From_dict(data: dict) -> Job:
        """ Creates a job from a dictionary
        """

        tasks = [
            Task.From_dict(j)
            for j in data.get("tasks", [])
        ]

        return Job(
            id=data["id"],
            name=data.get("name", ""),
            requires=data.get("requires", []),
            tasks=tasks,
        )