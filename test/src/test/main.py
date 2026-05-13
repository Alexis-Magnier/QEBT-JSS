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


    # plt.ion()
    # pos = nx.spring_layout(G)
    # nx.draw(G, pos, with_labels=True, node_size=1000, font_size=10)
    # edge_labels = nx.get_edge_attributes(G, 'label')
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    # plt.show()
    
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


def a():
    import yaml
    from .main import TEST_PROJECT_ROOT

    with open(TEST_PROJECT_ROOT / "data/mitsubishi-precedence-map.yaml") as stream:
        data = yaml.safe_load(stream)

    name = data["name"]
    version = data["version"]

    jobs = dict()
    for j in data["components"]:
        jobs[j["name"]] = {
            "name": j["name"],
            "id": j["id"],
            "requires": j["requires"]
        }
    
    for j in jobs.values():
        r = [jobs[req]["id"] for req in j["requires"]]
        j["requires"] = r
    
    jobs = {
        j["id"]: {
            "name": j["name"],
            "requires": j["requires"],
            "tasks": []
        }
        for j in jobs.values()
    }

    data = {
        "precedence-map": {
            "name": name,
            "version": version,
            "jobs": jobs
        }
    }

    print(data)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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


    states: dict[dict] = {
        frozenset(): {
            "id": 0,
            "jobs": {
                s.start for s in p.sequences.values()
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

    render_states = [s["id"] for s in states.values()]
    transitions = []

    for state in states.values():

        for job, j in state["children"]:
            next = states.get(j, None)
            if not next: continue
            transitions.append((state["id"], next["id"], job.name))

    for t in transitions:
        print(t)

    render_graph(render_states, transitions)
