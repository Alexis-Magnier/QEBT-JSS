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
    from pyvis.network import Network


    G = nx.DiGraph()

    for state in states:
        G.add_node(state, label=str(state))

    for source, target, arc in transitions:
        G.add_edge(source, target, label=arc)
    

    net = Network(notebook=False, directed=True)
    net.from_nx(G)

    net.set_options("""
{
  "layout": {
    "hierarchical": {
      "enabled": true,
      "direction": "UD",
      "sortMethod": "directed"
    }
  }
}
""")
    
    net.show("graph.html", notebook=False)

    
def main():
    print(TEST_PROJECT_ROOT)
    import converter
    import dispatcher

    with open(TEST_PROJECT_ROOT / "data/resources.json") as file:
        resources = ResourceRegistry.From_dict(json.load(file)["resources"])

    solution = converter.Solution.From_sol(
        TEST_PROJECT_ROOT / "data/solution.sol",
        resources,
    )

    d = dispatcher.Dispatcher.From_solution(
        solution,
        resource_filter=[resources.get("H")]
    )

    for op in d.operations:
        print(op)

    result = d.generate_domain_pddl(TEST_PROJECT_ROOT / "data/templates/", "domain.pddl.j2")

    #print(result)

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

    p = load_sequenceGraph(TEST_PROJECT_ROOT / "data/data.json")
    policies = load_policies(TEST_PROJECT_ROOT / "data/disassembly-policy-table.json")

    stateSpace = StateSpaceGraph.From_SequenceGraph(p)

    render_states = [s for s in stateSpace.states.keys()]
    transitions = []

    for id, s in stateSpace.states.items():
        transitions.extend([
            (id, c[1].id, c[0].name)
            for c in s.children
        ])

    
    print(len(transitions))
    print(len(render_states))
