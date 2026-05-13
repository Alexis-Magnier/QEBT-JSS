#!/usr/bin/env python
# -*- coding: utf-8 -*-

import converter

class Dispatcher:
    operation: list[tuple]

    @staticmethod
    def _Generate_operations_from_sol(
            sol:converter.Solution,
            resource_filter:list[str] = []
        ) -> list[tuple[str, converter.Operation, converter.OperationData]]:

        operations = list[tuple[str, converter.Operation, converter.OperationData]]()

        for op, data in sol.operations.items():

            # skip filtered out resources
            if op.resource in resource_filter:
                continue
            
            op_name = f"OP_{op.job}{op.operation}{op.resource.operation_suffix}"
            operation = (op_name, op, data)
            operations.append(operation)


        operations.sort(key=lambda x: x[2].start_time)

        # push wait actions
        i = 0  
        previous_end_time = None

        while i < len(operations):
            name, op, data = operations[i]

            if previous_end_time is not None and data.start_time > previous_end_time:
                operations.insert(i, (
                    f"wait", op, converter.OperationData(
                        start_time=previous_end_time,
                        end_time=data.start_time,
                        active=False
                    )
                ))
            previous_end_time = data.end_time
            i += 1
        
        return operations

    @staticmethod
    def From_solution(
            sol:converter.Solution,
            resource_filter:list[str] = []
        ) -> Dispatcher:
        
        operations = Dispatcher._Generate_operations_from_sol(sol, resource_filter)

        for op in operations:
            print(op)
                    

    def generate_domain_pddl(self):
        pass

    def generate_problem_pddl(self):
        pass