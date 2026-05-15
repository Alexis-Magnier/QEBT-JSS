#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from enum import IntFlag, auto
from collections import deque
from .types import *
from .Job import Job

@dataclass()
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
    probability: float = 1.0

    def update_probability(self):
        self.probability = 1.0
        for j in self.jobs:
            self.probability *= j.probability

    def __hash__(self):
        return self.id


class PrecedenceMapFlags(IntFlag):
    NONE = 0
    JOBS_LINKED = auto() # Wether the jobs have been linked together
    ACYCLIC = auto()
    GROUPED = auto()


@dataclass
class SequenceGraph:
    # meta
    id: PrecedenceMapID = INVALID_PRECEDENCE_MAP_ID
    name: str = ""
    flags: PrecedenceMapFlags = PrecedenceMapFlags.NONE

    # Content
    jobs: dict[JobID, Job] = field(default_factory=dict)
    sequences: dict[SequenceID, Sequence] = field(default_factory=dict)

    def is_acyclic(self):
        # 1. Compute in-degree
        in_degree = {
            job: len(job.previous)
            for job in self.jobs.values()
        }

        # 2. Start with nodes that have no dependencies
        queue = deque(self.root_jobs())

        visited_count = 0

        # 3. Process graph
        while queue:
            current = queue.popleft()
            visited_count += 1

            for next in current.next:
                in_degree[next] -= 1
                if in_degree[next] == 0:
                    queue.append(next)

        # 4. If we didn't visit all nodes → cycle exists
        acyclic = visited_count == len(self.jobs)

        return acyclic

    def root_jobs(self) -> list[Job]:
        roots = []
        for j in self.jobs.values():
            if len(j.previous) == 0:
                roots.append(j)
        
        return roots

    def compute_job_links(self) -> None:
        for job in self.jobs.values():
            job.previous = list(map(
                lambda n : self.jobs[n], job.requirments
            ))

            for p in job.previous:
                p.next.append(job)

    def job_groups(self) -> None:
        for job in self.jobs.values():
            s = Sequence(
                id=job.id,
                name=job.name,
                jobs=[job],
                start=job,
                end=job,
                previous=[],
                next=[]
            )

            job.sequence = s
            self.sequences[job.id] = s
        
        for job in self.jobs.values():
            sequence = job.sequence

            sequence.previous = [
                p.sequence for p in job.previous
            ]

            sequence.next = [
                n.sequence for n in job.next
            ]

    def group(self) -> None:
        self.sequences.clear()

        q = deque[Job](self.root_jobs())
        visited = set[Job]()
        i=0

        while len(q) != 0:
            current = q.pop()

            if current in visited: continue
            visited.add(current)

            # setup variables
            parent = None

            # If current job has a single parent
            if len(current.previous) == 1:
                parent = current.previous[0]
   
            if parent and len(parent.next) == 1:
                sequence = parent.sequence
            else:
                sequence = Sequence(id=i)
                self.sequences[i]=sequence
                sequence.start = current
                i+=1
            
            # update information
            sequence.end = current
            current.sequence = sequence
            sequence.jobs.append(current)

            # push children
            q.extend(current.next)
        
        # linking the sequences
        for s in self.sequences.values():

            s.next = [
                children.sequence
                for children in s.end.next 
            ]

            s.name = "-".join(
                [j.name for j in s.jobs]
            )

            for next in s.next:
                next.previous.append(s)
    
    def update_probabilities(self):
        for s in self.sequences.values():
            s.update_probability()


    @staticmethod
    def From_dict(data: dict) -> SequenceGraph:
        jobs = {
            int(id): Job.From_dict(int(id), data)
            for id, data in data.get("jobs", dict()).items()
        }

        return SequenceGraph(
            id = data.get("id"),
            name = data.get("name", ""),
            jobs=jobs
        )