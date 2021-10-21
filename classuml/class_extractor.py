from pathlib import Path
from typing import List
from dataclasses import dataclass

import astroid
from astroid import decorators


@dataclass
class FunctionData:
    name: str
    return_type: str

    @classmethod
    def from_function_def(cls, func_def: astroid.FunctionDef) -> "FunctionData":
        try:
            d = {}
            d["name"] = func_def.name
            # d["return_type"] = "" if not func_def.returns else func_def.returns.name
            d["return_type"] = (
                "" if not func_def.returns else func_def.returns.as_string()
            )
            return cls(**d)
        except Exception as e:
            print(func_def.as_string())
            raise e


@dataclass
class ClassData:
    name: str
    methods: List[FunctionData]
    decorators: List[str]
    basenames: List[str]

    @classmethod
    def from_class_def(cls, class_def: astroid.ClassDef) -> "ClassData":
        """ """
        d = {}
        d["name"] = class_def.name
        d["basenames"] = class_def.basenames
        d["methods"] = [
            FunctionData.from_function_def(f) for f in class_def.mymethods()
        ]
        # TODO: handle decorator Calls, e.g. @some_dec_func(param=val)
        d["decorators"] = (
            []
            if class_def.decorators is None
            else [
                dec.name
                for dec in class_def.decorators.nodes
                if isinstance(dec, astroid.Name)
            ]
        )

        return cls(**d)


class ClassExtractor:
    """Extracts classes from a module."""

    def __init__(self, filepath: Path, module: astroid.Module) -> None:
        self.filepath = filepath
        self.module = module

        class_defs = [e for e in self.module.body if isinstance(e, astroid.ClassDef)]

        self.classes: List[ClassData] = [
            ClassData.from_class_def(c) for c in class_defs
        ]
