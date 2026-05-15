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
    parents: list[tuple[Sequence, State]] = field(default_factory=list)
    probability: float = 1.0

    def to_dict(self) -> dict:
        return {
            "children": {
                state.id: sequence.id
                for sequence, state in self.children
            }
        }

    def __hash__(self):
        return self.id

@dataclass
class StateSpaceGraph:
    states: dict[int, State] = field(default_factory=dict)

    def foreach_dfs(self, fn):
        q = deque[State](
            [
                s for s in self.states.values()
                if len(s.parents) == 0

            ]
        )

        visited = set[State]()

        while q:
            current = q.popleft()

            if not set([p[1] for p in current.parents]) <= visited:
                continue

            if current in visited:
                continue
            visited.add(current)

            fn(current)

            q.extend([c[1] for c in current.children])


    def update_probabilities(self):

        def update_prob(s:State):

            if len(s.parents) == 0:
                s.probability = 1
                return
            
            fail = 1.0

            p = 0
            for sequence, parent in s.parents:
                p += (parent.probability * sequence.probability) / len(parent.children)

            s.probability = p

        self.foreach_dfs(update_prob)

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

            for sequence, s2 in children:
                s2.parents.append((sequence, state))

            state.children = children

        return StateSpaceGraph(
            states = states2
        )
    

    def to_dict(self) -> dict:
        return {
            "states": {
                i: s.to_dict()
                for i, s in self.states.items()
            }
        }