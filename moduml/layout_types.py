from typing import List
from pathlib import Path
import re

import networkx as nx
import pydot
import astroid

from .module.interface import ModuleInterface
from .module import interface


def _is_package(graph: nx.DiGraph, node: Path) -> bool:
    """ if a node has a successor that is an __init__.py file
    """
    s: Path
    for s in graph.successors(node):
        if s.relative_to(node).as_posix() == "__init__.py":
            return True
    return False


class EdgeLayout(pydot.Edge):
    """ Dot layout for an edge.
    """
    def __init__(self, src: Path, dst: Path, **kwargs) -> None:
        super().__init__(
            src=pydot.Node(src.as_posix()), 
            dst=pydot.Node(dst.as_posix()),
            **kwargs
            )


class DirLayout(pydot.Node):
    """ Dot layout for a directory node.
    """
    def __init__(self, 
                 graph: nx.DiGraph, 
                 node: Path
                 ) -> None:
        super().__init__(name=node.as_posix())
        if _is_package(graph=graph, node=node): self.set("shape", "component")
        else: self.set("shape", "folder")
        self.set("color", "red")
        self.set("label", node.relative_to(node.parent).as_posix())


class FileLayout(pydot.Node):
    """ Dot layout for a file node.
    """
    def __init__(self, 
                 node: Path, 
                 with_interface: bool,
                 show_class_bases: bool = False,
                 show_func_decorators: bool = False,
                 show_func_return_type: bool = False
                 ) -> None:
        super().__init__(name=node.as_posix())
        self.set("shape", "record")
        filename = node.relative_to(node.parent).as_posix()
        if with_interface:
            mod_int: ModuleInterface = interface.get_module_interface(module_path=node)
            cs: List[str] = self._class_definition_style(class_defs=mod_int.class_defs, 
                                                         show_class_bases=show_class_bases)
            vs: List[str] = [v.name for v in mod_int.single_assignments]
            fs: List[str] = self._function_def_style(function_defs=mod_int.function_defs, 
                                                     show_func_decorators=show_func_decorators,
                                                     show_func_return_type=show_func_return_type)
            
            layout = f"{{ {filename}| {FileLayout.to_record_str(cs + vs)} | {FileLayout.to_record_str(fs)} }}"
            self.set(
                "label", 
                layout
                )
        else:
            self.set("label", filename)

    def _class_definition_style(self, class_defs: List[astroid.ClassDef], show_class_bases: bool) -> List[str]:
        """ Format class names with or without it's bases.
                E.g. 'Class1()' or 'Class1(Foo, Bar)'
        """
        classes_with_bases = []
        bases = []
        for c in class_defs:
            if show_class_bases:
                bases = [base.as_string() for base in c.bases]
            classes_with_bases.append( f"{c.name}({', '.join(bases)})")
        return classes_with_bases

    def _function_def_style(self, 
                            function_defs: List[astroid.FunctionDef], 
                            show_func_decorators: bool, 
                            show_func_return_type: bool
                            ) -> List[str]:
        """ Format function names with or without return type string.
                E.g. 'func' or 'func: int'
        """
        # return type string pattern
        # match group between '->' (remove whitespace) and ':' 
        # e.g. def bla(a,b) -> int: ... --> 'int'
        pattern = "->\s*(.*):"
        fs = []
        for func_def in function_defs:
            # NOTE: decorators are added as a new "function" layout-wise before the function,
            #       ergo this has to be first.
            # if show decorators AND has decorators
            if show_func_decorators and func_def.decorators:
                deco_strings = []
                for d in func_def.decorators.nodes:
                    deco_strings.append(d.as_string())
                deco_string = "@ " + ", ".join(deco_strings)
                fs.append(deco_string)
            
            func_name = func_def.name
            # if show return type AND function has a defined return type
            if show_func_return_type and func_def.returns:
                return_type_str = re.findall(pattern, func_def.as_string())[0]
                func_name += f": {return_type_str}"

            fs.append(func_name)
        return fs

    @staticmethod
    def to_record_str(lst: List[str]) -> str:
        """ Convert a list of strings to a single string in the dot record format.
            E.g.: attr1\lattr2\l --> attr1 | attr2
        """
        return "\l".join(lst) + "\l"

