#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Any

from .types import *
from .Policy import Query

NAME_ENTRY = "name"
PROPERTY_ENTRY = "props"
QUERY_ENTRY = "query"

@dataclass
class Task:
    id: TaskID = INVALID_TASK_ID
    name: str = ""

    props: dict[str, Any] = field(default_factory=dict)

    query: Query = None 
 
    @staticmethod
    def From_dict(id:int, data: dict) -> Task:
        return Task(
            id=id,
            name=data.get(NAME_ENTRY, ""),
            props=data.get(PROPERTY_ENTRY, dict()),

            query=Query.From_dict(query_data)
            if (query_data := data.get(QUERY_ENTRY, None)) is not None else None
        )