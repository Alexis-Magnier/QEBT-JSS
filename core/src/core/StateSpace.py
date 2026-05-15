#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from .Job import Job
from .SequenceGraph import SequenceGraph
from collections import deque

@dataclass
class State:
    id: int
    children: list[tuple[Job, State]] = field(default_factory=list)

@dataclass
class StateSpaceGraph:
    states: dict[int, State] = field(default_factory=dict)

    @staticmethod
    def From_SequenceGraph(graph: SequenceGraph) -> StateSpaceGraph:
        states: dict[frozenset, dict] = {
            frozenset(): {
                "id": 0,
                "jobs": {
                    s.start for s in graph.sequences.values()
                    if len(s.previous) == 0
                },
                "children": []
            }
        }

        # (state, job)
        queue = deque[int]([i for i in states.keys()])
        visited = set()

        i=1
        while queue:
            done = frozenset(queue.pop())

            if done in visited:
                continue
            visited.add(done)

            current = states[done]

            for job in current["jobs"]:

                previous = set([j.id for j in job.previous])

                # if the jobs are
                if not previous <= done:
                    continue
                    
                new_done = done | {job.id}

                if new_done not in states:
                    next_jobs = (current["jobs"] - {job}) | set(job.next)

                    i+=1
                    
                    states[new_done] = {
                        "id": i,
                        "jobs": next_jobs,
                        "children": []
                    }


                    queue.append(new_done)
                
                current["children"].append((job, new_done))
        
        states2: dict[int, State] = {
            s["id"]: State(
                id=s["id"]
            )
            for s in states.values()
        }

        for s in states.values():
            id = s["id"]
            state = states2[id]

            children = [
                (job, states2[next["id"]])
                for job, done in s["children"]
                if (next := states.get(done, None)) is not None
            ]

            state.children = children

        return StateSpaceGraph(
            states = states2
        )