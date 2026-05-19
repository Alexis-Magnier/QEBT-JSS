#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import math
import numpy as np

from .Policy import Policy
from .types import *
from .Query import Query
from .QueryResult import QueryResult


POLICIES_NODE = "policies"


def cosine_similarity(a: dict[str, float], b: dict[str, float], weights: dict[str, float]) -> float:
    # Union of all keys
    keys = set(a) | set(b)

    # Build vectors
    va = np.array([a.get(k, 0.0) for k in keys])
    vb = np.array([b.get(k, 0.0) for k in keys])
    ws = np.array([weights.get(k, 1.0) for k in keys])

    # Dot product
    dot = np.sum(va * vb * ws)

    # Magnitudes
    norm_a = math.sqrt(np.sum(np.square(va)))
    norm_b = math.sqrt(np.sum(np.square(vb)))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)

def similarity_score(a: dict[str, float], b: dict[str, float], weights: dict[str, float]) -> float:
    seta = set(a)
    setb = set(b)

    keys = seta | setb
    missing = seta.difference(setb)

    va = np.array([a.get(k, 0.0) for k in keys])
    vb = np.array([b.get(k, 0.0) for k in keys])
    ws = np.array([weights.get(k, 1.0) for k in keys])

    distance = np.sum(np.abs(va - vb) * ws)

    return 1/distance

@dataclass
class PolicyTable:

    policies: dict[int, Policy] = field(default_factory=list)
    
    @staticmethod
    def From_dict(data:dict) -> PolicyTable:
        try:
            policies = {
                int(id): Policy.From_dict(int(id), policy)
                for id, policy in data[POLICIES_NODE].items()
            }
        except KeyError as e:
            raise Exception("Could not find the \"%s\" data entry" % POLICIES_NODE)
        except AttributeError as e:
            raise Exception("Data is ill-formated. Expected \"%s\" to be a dictionary (%s)" % (POLICIES_NODE, e))

        return PolicyTable(
            policies=policies
        )

    def query(self, query:Query, similarity_func=cosine_similarity, remap=False) -> QueryResult:
        """
        query(query, similarity_func (default=cosine_similarity), remap (default=False))

        Assignes a similarity score to each of the registred policies

        Parameters
        ----------
        query : Query
            The query itself, describing wanted descriptors, domains and weights

        similarity_func : function, default=cosine_similarity
            Assignes a similarity score between the policy's descriptors and the query's.

            >>> def foo(a: dict[str, float], b: dict[str, float], weights: dict[str, float]) -> float
        
        remap : bool, default=False
            Remaps the scores on a [-1, 1] range.


        Returns
        ----------
        A QueryResult instance

        """
        p = list()

        for policy in self.policies.values():
            
            # Check if the query domains is a subset or equal to the policy domains
            if not policy.domains >= query.domains:
                continue

            
            # Descriptor similarity
            sim = similarity_func(policy.descriptors, query.descriptors, query.weights)
            
            p.append((policy, sim))
        
        
        if remap:
            max_score = -math.inf
            min_score = math.inf

            for policy, score in p:
                if score > max_score:
                    max_score = score
                
                if score < min_score:
                    min_score = score

            p = [(policy, 2 * (score - min_score) / (max_score - min_score) - 1) for policy, score in p]

        # Sort from highest score to lowest
        p.sort(key=lambda x: x[1], reverse=True)

        return QueryResult(
            result = p
        )