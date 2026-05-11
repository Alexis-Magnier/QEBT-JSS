#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from enum import IntFlag, auto
from collections import deque
from .types import *
from .Job import Job
from .Sequence import Sequence

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
                lambda n : self.jobs[n], job.requires
            ))

            for p in job.previous:
                p.next.append(job)

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

            for next in s.next:
                next.previous.append(s)


    @staticmethod
    def From_dict(data: dict) -> SequenceGraph:
        jobs = {
            j["id"]: Job.From_dict(j)
            for j in data.get("jobs", [])
        }

        return SequenceGraph(
            id = data.get("id"),
            name = data.get("name", ""),
            jobs=jobs,
        )