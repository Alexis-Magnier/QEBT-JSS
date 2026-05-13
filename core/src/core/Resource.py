#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Resource:
    id: int
    name: str
    acronym: str
    exclusive: tuple[str]

    @staticmethod
    def From_dict(id:int, data:dict) -> Resource:
        name = data["name"]

        return Resource(
            id=id,
            name=name,
            acronym=data.get("acronym", name[0]),
            exclusive=tuple(data.get("exclusiveWith", ()))
        )


@dataclass
class ResourceRegistry:
    resources: dict[int, Resource] = field(default_factory=dict)

    def get_from_acronym(self, acronym:str) -> Resource:
        try:
            return next(n for n in self.resources.values() if n.acronym == acronym)
        except StopIteration as e:
            raise IndexError(f"No resource acronym is \"{acronym}\"")


    @staticmethod
    def From_dict(data:dict) -> ResourceRegistry:
        return ResourceRegistry(
            resources = {
                int(id): Resource.From_dict(int(id), d)
                for id, d in data["resources"].items()
            }
        )
