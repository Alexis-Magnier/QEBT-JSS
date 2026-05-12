#!/usr/bin/env python
# -*- coding: utf-8 -*-

import converter

class Dispatcher:

    @staticmethod
    def From_solution(sol:converter.Solution) -> Dispatcher:
        
        for op in sol.operations.keys():
            suffix = "_CO" if op.resource == converter.Resource.COLLABORATIVE else ""

            op_name = f"OP_{op.job}{op.operation}{suffix}"
            print(op_name)

    def generate_domain_pddl(self):
        pass

    def generate_problem_pddl(self):
        pass