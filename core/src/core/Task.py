#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Any

from .types import *
from .Policy import Query

@dataclass
class Task:
    id: TaskID = INVALID_TASK_ID
    name: str = ""

    props: dict[str, Any] = field(default_factory=dict)

    query: Query = None 
 
    @staticmethod
    def From_dict(data: dict) -> Task:
        return Task(
            id=data.get("id"),
            name=data.get("name", ""),
            props=data.get("props", dict()),

            query=Query.From_dict(query_data)
            if (query_data := data.get("query", None)) is not None else None
        )