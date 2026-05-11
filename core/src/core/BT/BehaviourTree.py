#!/usr/bin/env python
# -*- coding: utf-8 -*-

import py_trees

class BehaviourTree(py_trees.trees.BehaviourTree):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ""

        py_trees.decorators
        

    def From_dict(data:dict) -> BehaviourTree:
        name = data.get("name", "unamed behaviour tree")