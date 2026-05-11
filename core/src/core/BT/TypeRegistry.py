#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from pydoc import locate

@dataclass
class TypeProperty:
    name: str
    description: str
    type = None
    

    @staticmethod
    def From_dict(name:str, data:dict) -> TypeProperty:

        t = None
        if (typename := data["type"]) is not None:
            t = locate(typename)
        else:
            print("Unkown type %s" % typename)

        return TypeProperty(
            name=name,
            type=t,
            description=data.get("description", "")
        )

@dataclass
class TypeChoice:
    name: str
    object = None
    properties: dict[str, TypeProperty] = field(default_factory=dict)

    @staticmethod
    def From_dict(name:str, data:dict) -> TypeChoice:

        source = data.get("source", "builtin")
        object_name = data["object"]

        if source == "builtin":
            object = locate(object_name)
        else:
            raise ValueError("Can only support \"builtin\" source")
        
        return TypeChoice(
            name=name,
            object=object,
            properties={
                n: TypeProperty.From_dict(n, d)
                for n, d in data.get("props", dict()).items()
            }
        )

@dataclass
class Type:
    name: str
    choices: dict[str, TypeChoice]

    @staticmethod
    def From_dict(name:str, data:dict) -> Type:
        return Type(
            name=name,
            choices={
                n: TypeChoice.From_dict(n, d)
                for n, d in data.get("choices", dict()).items()
            }
        )

@dataclass
class TypeRegistry:
    types: dict[str, Type] = field(default_factory=dict)

    def merge(self, other:TypeRegistry) -> None:
        for n, t in other.types.items():
            pass

    @staticmethod
    def From_dict(data:dict) -> TypeRegistry:
        return TypeRegistry(
            types = {
                n: Type.From_dict(n, d)
                for n, d in data.get("types", dict()).items()
            }
        )
