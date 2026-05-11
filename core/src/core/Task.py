#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from .types import *
from .Policy import Query

@dataclass
class Task:
    id: TaskID = INVALID_TASK_ID
    name: str = ""

    query: Query = None 
 
    @staticmethod
    def From_dict(data: dict) -> Task:
        return Task(
            id=data.get("id"),
            name=data.get("name", ""),

            query=Query.From_dict(query_data)
            if (query_data := data.get("query", None)) is not None else None
        )