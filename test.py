from pathlib import Path
from collections import deque
import json

from core import *

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

p = load_sequenceGraph("./data/simple-sequence-graph.json")
policies = load_policies("./data/disassembly-policy-table.json")

queue = deque[Job]()
visited = set[Job]()

for sequence in p.sequences.values():
    if len(sequence.previous) == 0:
        queue.append(sequence.start)

while len(queue) != 0:
    current = queue.pop()

    if not set(current.previous) <= visited:
        continue 

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