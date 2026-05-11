#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from .Job import JobID, INVALID_JOB_ID
from typing import  NewType
from .types import *

@dataclass
class Sequence:
    # Identification
    id: SequenceID = INVALID_SEQUENCE_ID
    name: str = ""

    # Content
    jobs: list[JobID] = field(default_factory=list)
    start: JobID = INVALID_JOB_ID
    end: JobID = INVALID_JOB_ID

    previous: list[SequenceID] = field(default_factory=list)
    next: list[SequenceID] = field(default_factory=list)

    @staticmethod
    def From_dict(data: dict) -> Sequence:
        """ Creates a job from a dictionary
        """
        return SequenceID(
            id=data["id"],
            name=data.get("name", ""),
            jobs=data.get("jobs", []),
        )

    def to_dict(self) -> Sequence:
        return {
            "id": self.id,
            "name": self.name,
            "jobs": self.jobs
        }

    
