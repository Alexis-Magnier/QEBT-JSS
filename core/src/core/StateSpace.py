#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import TypedDict

from .Sequence import Sequence
from .Sequence import SequenceGraph
from collections import deque

@dataclass
class State:
    id: int
    children: list[tuple[Sequence, State]] = field(default_factory=list)

@dataclass
class StateSpaceGraph:
    states: dict[int, State] = field(default_factory=dict)

    @staticmethod
    def From_SequenceGraph(graph: SequenceGraph) -> StateSpaceGraph:
        class StateData(TypedDict):
            id: int
            sequences: list[Sequence]
            children: tuple[Sequence, frozenset]
        

        states: dict[frozenset, StateData] = {
            frozenset(): {
                "id": 0,
                "sequences": {
                    s for s in graph.sequences.values()
                    if len(s.previous) == 0
                },
                "children": []
            }
        }

        queue = deque[frozenset]([i for i in states.keys()])
        visited = set()

        i=1
        while queue:
            done = frozenset(queue.pop())

            # Skip visited entries
            if done in visited:
                continue
            visited.add(done)

            # query current state data
            current = states[done]

            for sequence in current["sequences"]:

                previous = set([s.id for s in sequence.previous])

                # if the sequence prerequisits are not met. We skip it
                if not previous <= done:
                    continue
                    
                new_done = done | {sequence.id}

                if new_done not in states:
                    next_sequences = (current["sequences"] - {sequence}) | set(sequence.next)

                    i+=1
                    
                    states[new_done] = {
                        "id": i,
                        "sequences": next_sequences,
                        "children": []
                    }


                    queue.append(new_done)
                
                current["children"].append((sequence, new_done))
        
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
                (sequence, states2[next["id"]])
                for sequence, done in s["children"]
                if (next := states.get(done, None)) is not None
            ]

            state.children = children

        return StateSpaceGraph(
            states = states2
        )