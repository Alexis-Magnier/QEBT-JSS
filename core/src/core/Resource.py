#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Resource:
    id: int
    name: str
    exclusive: tuple[str]
    operation_suffix: str

    @staticmethod
    def From_dict(id:str, data:dict) -> Resource:

        return Resource(
            id=id,
            name=data["name"],
            exclusive=tuple(data.get("exclusiveWith", ())),
            operation_suffix=data.get("operation_suffix", "")
        )


@dataclass
class ResourceRegistry:
    resources: dict[str, Resource] = field(default_factory=dict)

    def get(self, id:str) -> Resource:
        return self.resources[id]

    @staticmethod
    def From_dict(data:dict) -> ResourceRegistry:
        return ResourceRegistry(
            resources = {
                id: Resource.From_dict(id, d)
                for id, d in data["resources"].items()
            }
        )
