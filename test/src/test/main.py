#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from collections import deque
import json

from core import *


from pathlib import Path
TEST_PROJECT_ROOT = Path(__file__).resolve().parents[2]

def render_graph(states, transitions):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()
    for source, actions in transitions.items():
        for action, targets in actions.items():
            for target, prob in targets.items():
                G.add_edge(source, target, label=f"{action}\n{prob}")
    
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=1000, font_size=10)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()
    
def main():
    print(TEST_PROJECT_ROOT)


    temp()


def temp():
    def load_sequenceGraph(path:Path) -> SequenceGraph:
        with open(path, "r") as file:
            data = json.load(file)
        
        m = data["precedence-map"]

        p = SequenceGraph.From_dict(m)
        p.compute_job_links()

        if not p.is_acyclic():
            raise Exception("the jobs must be acyclic")

        p.group()
        return p


    def load_policies(path:Path) -> PolicyTable:
        with open(path) as file:
            policies = PolicyTable.From_dict(json.load(file)["policy-base"])
        
        return policies

    p = load_sequenceGraph(TEST_PROJECT_ROOT / "data/simple-sequence-graph.json")
    policies = load_policies(TEST_PROJECT_ROOT / "data/disassembly-policy-table.json")

    queue = deque[Job]()
    visited = set[Job]()

    for sequence in p.sequences.values():
        if len(sequence.previous) == 0:
            queue.append(sequence.start)

    states = ['S0', 'S1']
    transitions = {
        'S0': {'stay': {'S0': 0.9, 'S1': 0.1}, 'move': {'S1': 1.0}}
    }

    while len(queue) != 0:
        current = queue.pop()

        if not set(current.previous) <= visited:
            continue 
        
        states.append(current.id)
        visited.add(current)
        print("job %d : %s" % (current.id, current.name))

        for task in current.tasks:
            r = policies.query(task.query)

            if len(r.result) == 0:
                print("no policy found for ", task.query)
                continue

            policy, score = r.result[0]
            print("\t- %s : %s (similarity: %0.2f)" % (task.name, policy.name, score))

        queue.extend(current.next)

    
    # Example structure
    
    render_graph(states, transitions) # Run this to visualize
