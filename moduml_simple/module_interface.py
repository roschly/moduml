from dataclasses import dataclass
from typing import List
from pathlib import Path

import astroid


@dataclass
class ModuleInterface:
    class_defs: List[astroid.ClassDef]
    function_defs: List[astroid.FunctionDef]
    single_assignments: List[astroid.AssignName]


def _get_single_assignments(m: astroid.Module) -> List[astroid.AssignName]:
    """Returns single assignments in top scope of a module.
    Only include single assignment.
    E.g. "a = 11", where the first element/child if of type AssignName (= "a").
    Ignore tuple case: "a, b = some_func()".
    """
    assigns = [e for e in m.body if isinstance(e, astroid.Assign)]
    single_assigns = [
        list(a.get_children())[0]
        for a in assigns
        if isinstance(list(a.get_children())[0], astroid.AssignName)
    ]
    return single_assigns


def get_module_interface(module: astroid.Module) -> ModuleInterface:
    return ModuleInterface(
        class_defs=[e for e in module.body if isinstance(e, astroid.ClassDef)],
        function_defs=[e for e in module.body if isinstance(e, astroid.FunctionDef)],
        single_assignments=_get_single_assignments(m=module),
    )
