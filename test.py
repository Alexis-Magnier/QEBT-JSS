from pathlib import Path
import json

import core
from core import SequenceGraph 

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


def load_policies(path:Path) -> core.PolicyTable:
    with open(path) as file:
        policies = core.PolicyTable.From_dict(json.load(file)["policy-base"])
    
    return policies

p = load_sequenceGraph("./data/simple-sequence-graph.json")
policies = load_policies("./data/policy-table.json")

q = core.Query(
    domains={"Attack"},
    descriptors={
        "world.difficulty": 0.5,
        "player.bored": True,
        "this.health": 0.63,
        "this.defensive": 0.9,
        "this.aggresive": 0.1,
        "this.underAttack": False
    },
    similarity={
        "this.defensive": 1
    }
)

from core.Policy.PolicyTable import similarity_score, cosine_similarity

r = policies.query(q, similarity_func=cosine_similarity)
print("\n".join([f"{p.name} : {s}" for p, s in r.result]))


print(
    "\n".join([
        f" \
{s.id} \
{[p.id for p in s.previous]} \
{[n.id for n in s.next]} \
{[f"{j.name}, t:{j.tasks}" for j in s.jobs]} \
        "
        for s in p.sequences.values()
    ])
)