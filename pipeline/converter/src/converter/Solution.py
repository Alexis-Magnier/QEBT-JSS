#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from pathlib import Path
from .Operation import Operation, OperationData

@dataclass
class Solution:
    operations: dict[Operation, OperationData] = field(default_factory=dict)

    @staticmethod
    def From_sol(path: Path) -> Solution:
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
                if not line.startswith(("Sijk", "Cijk", "Xijk")):
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

                match variable_name:
                    case "Sijk":
                        data.start_time = value
                    case "Cijk":
                        data.end_time = value
                    case "Xijk" if value > 0.5:
                        data.active = True

            # filter out operation which duration is nil
            solution = {
                operation: data
                for operation, data in solution.items()
                if data.duration() > 0 and data.active
            }

            # This functions checks if the operation is already handled by a collaborative operation
            def is_handled_by_collaborative(op: Operation):
                collaborative_variant = Operation(
                    job = op.job,
                    operation = op.operation,
                    resource = 'Co'
                )

                return collaborative_variant in solution

            solution = {
                op: data
                for op, data in solution.items()
                if op.resource == 'Co' or not is_handled_by_collaborative(op)
            }

            return Solution(
                operations=solution
            )