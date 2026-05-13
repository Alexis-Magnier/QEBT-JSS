#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from pathlib import Path
from .Operation import Operation, OperationData
import core

@dataclass
class Solution:
    operations: dict[Operation, OperationData] = field(default_factory=dict)

    @staticmethod
    def From_sol(path: Path, resources: core.ResourceRegistry) -> Solution:

        def set_start_time(data: OperationData, value:float):
            data.start_time = value

        def set_end_time(data: OperationData, value:float):
            data.end_time = value

        def set_active(data: OperationData, value:float):
            data.active = value > 0.5

        VALUE_TO = {
            "Sijk": set_start_time, 
            "Cijk": set_end_time, 
            "Xijk": set_active, 
        }

        with open(path, "rt") as file:
            solution: dict[Operation, OperationData] = dict()

            """
            Each line of the sol file is formated as:

                <variable>[<operation>,<job>,<resource>] <value>

            for instance, 'Xijk[op_6,j_2,H] 0'
            
            """

            # for each stripped line of the file
            while (line := file.readline().strip()):
                # if the file doesn't start with "Sijk", "Cijk" or "Xijk" : skip
                if not line.startswith(tuple(VALUE_TO.keys())):
                    continue
                
                # extract the variable from the value
                parts = line.split(' ')

                variable = parts[0]
                value = round(float(parts[1]), 3)
                
                # find the '[' ']' characters
                a = variable.find('[')
                b = variable.rfind(']')

                # extract the content between '[' and ']' and split it for every ','
                inside = variable[a + 1:b]
                operation, job, resource = inside.split(',')

                job = job[job.find('_')+1:]
                operation = operation[operation.find('_')+1:]

                resource = resources.get(resource)

                # extract the variable name "Sijk", "Cijk" or "Xijk"
                variable_name = variable[0:a]

                op = Operation(
                    job = job,
                    operation = operation,
                    resource = resource
                )

                data = solution.get(op)
                if data is None:
                    data = solution[op] = OperationData()

                VALUE_TO[variable_name](data, value)

            # filter out operation which duration is nil
            solution = {
                operation: data
                for operation, data in solution.items()
                if data.duration() > 0 and data.active
            }

            # This functions checks if the operation is already handled by a collaborative operation
            def is_exlusive_or_not_by_exclusive(op: Operation):
                if len(op.resource.exclusive) > 0:
                    return True

                candidates = []
                for r in resources.resources.values():

                    # Skip non exclusive resources
                    if not op.resource.id in r.exclusive:
                        continue

                    candidates.append(r)

                for r in candidates:
                    collaborative_variant = Operation(
                        job = op.job,
                        operation = op.operation,
                        resource = r
                    )

                    if collaborative_variant in solution:
                        return False
                    
                return True

            solution = {
                op: data
                for op, data in solution.items()
                if is_exlusive_or_not_by_exclusive(op)
            }

            return Solution(
                operations=solution
            )
        
    @staticmethod
    def From_dict(data:dict) -> Solution:
        return Solution(
            operations = {
                Operation.From_string(op): OperationData.from_dict(data)
                for op, data in data.get(["operations"], dict())
            }
        )
    
    def to_dict(self) -> dict:
        return {
            "operations": {
                op.to_string(): data.to_dict()
                for op, data in self.operations.items()
            }
        }