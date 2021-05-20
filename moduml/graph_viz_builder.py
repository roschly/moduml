from typing import List
from pathlib import Path
import argparse
import re

import networkx as nx
import pydot
import astroid

from .module.interface import ModuleInterface
from .module import interface
from .module.imports import get_module_imports


# Global reference to program args, assigned from outside this module.
ARGS: argparse.Namespace = None


class EdgeLayout(pydot.Edge):
    """ Dot layout for an edge.
    """
    def __init__(self, src: Path, dst: Path) -> None:
        super().__init__(
            src=pydot.Node(src.as_posix()), 
            dst=pydot.Node(dst.as_posix()),
            color="gray",
            style="solid"
            )


class DirLayout(pydot.Node):
    """ Dot layout for a directory node.
    """
    def __init__(self, graph: nx.DiGraph, node: Path) -> None:
        super().__init__(name=node.as_posix())
        if _is_package(graph=graph, node=node): self.set("shape", "component")
        else: self.set("shape", "folder")
        self.set("color", "red")
        self.set("label", node.relative_to(node.parent).as_posix())


class FileLayout(pydot.Node):
    """ Dot layout for a file node.
    """
    def __init__(self, node: Path, with_interface: bool) -> None:
        super().__init__(name=node.as_posix())
        self.set("shape", "record")
        filename = node.relative_to(node.parent).as_posix()
        if with_interface:
            mod_int: ModuleInterface = interface.get_module_interface(module_path=node)
            cs: List[str] = self._class_definition_style(mod_int.class_defs)
            vs: List[str] = [v.name for v in mod_int.single_assignments]
            fs: List[str] = self._function_def_style(mod_int.function_defs)
            
            layout = f"{{ {filename}| {FileLayout.to_record_str(cs + vs)} | {FileLayout.to_record_str(fs)} }}"
            self.set(
                "label", 
                layout
                )
        else:
            self.set("label", filename)

    def _class_definition_style(self, class_defs: List[astroid.ClassDef]) -> List[str]:
        """ Format class names with or without it's bases.
                E.g. 'Class1()' or 'Class1(Foo, Bar)'
        """
        classes_with_bases = []
        bases = []
        for c in class_defs:
            if ARGS.show_class_bases:
                bases = [base.as_string() for base in c.bases]
            classes_with_bases.append( f"{c.name}({', '.join(bases)})")
        return classes_with_bases

    def _function_def_style(self, function_defs: List[astroid.FunctionDef]) -> List[str]:
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
            if ARGS.show_func_decorators and func_def.decorators:
                deco_strings = []
                for d in func_def.decorators.nodes:
                    deco_strings.append(d.as_string())
                deco_string = "@ " + ", ".join(deco_strings)
                fs.append(deco_string)
            
            func_name = func_def.name
            # if show return type AND function has a defined return type
            if ARGS.show_func_return_type and func_def.returns:
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



def _is_package(graph: nx.DiGraph, node: Path) -> bool:
    """ if a node has a successor that is an __init__.py file
    """
    s: Path
    for s in graph.successors(node):
        if s.relative_to(node).as_posix() == "__init__.py":
            return True
    return False


def _is_file(graph: nx.DiGraph, node: Path) -> bool:
    """ A leaf node, i.e. with no successor nodes, is a file.
    """
    return len(list(graph.successors(node))) == 0


def _parse_python_file(filepath: Path) -> astroid.Module:
    """ Parse a python file with astroid.
    """
    with open(filepath) as fh:
            code: str = fh.read()
    return astroid.parse(code)


def _handle_weird_pydot_name(cluster_node: Path) -> str:
    """ pydot.Node names appear to be wrapped in an extra layer of strings
            e.g. "dir1/file1.py" --> '"dir1/file1.py"'
        So, pass string through Node constructor and retrieve name, in order to replicate.
    """
    cluster_node_name = pydot.Node(name=cluster_node.as_posix()).get_name()
    return cluster_node_name


class GraphVizBuilder:
    def __init__(self, 
                 path_graph: nx.DiGraph, 
                 project_path: Path, 
                 rankdir: str = "TB"
                 ) -> None:
        self.rankdir = rankdir
        self.g = path_graph
        self.project_path = project_path

        self.file_nodes = [n for n in self.g.nodes if _is_file(graph=self.g, node=n)]
        self.dir_nodes = [n for n in self.g.nodes if not _is_file(graph=self.g, node=n)]

        self.reset()

    def reset(self) -> None:
        self._graph = pydot.Dot(graph_type="digraph", 
                                rankdir=self.rankdir,
                                fontname="Helvetica"
                                )
        self._graph.set_node_defaults(fontname="Helvetica")

    @property
    def graph(self) -> pydot.Dot:
        product = self._graph
        self.reset()
        return product

    def add_file_nodes(self, with_interface: bool = False) -> None:
        for n in self.file_nodes:
            node = FileLayout(node=n, with_interface=with_interface)
            self._graph.add_node(node)

    def add_dir_nodes(self) -> None:
        for n in self.dir_nodes:
            node = DirLayout(graph=self.g, node=n)
            self._graph.add_node(node)

    def add_dir_clusters(self) -> None:
        for n in self.dir_nodes:
            c = pydot.Cluster(n.as_posix(), 
                            #  label=n.relative_to(n.parent).as_posix(), 
                             label=n.as_posix(),
                             color="gray")
            # add nodes to cluster
            cluster_nodes = [s for s in self.g.successors(n) if _is_file(graph=self.g, node=s)]

            # find cluster nodes in _graph instead of g
            for c_node in cluster_nodes:
                c_node_name = _handle_weird_pydot_name(cluster_node=c_node)
                # returns a list, get first item 
                node_list = self._graph.get_node( c_node_name )
                assert len(node_list) == 1, "only one node should exist with given name"
                node = node_list[0]
                c.add_node(node)

            # add cluster to graph
            self._graph.add_subgraph(c)


    def add_hierarchy_links(self) -> None:
        for n in self.g.nodes:
            for s in self.g.successors(n):
                edge = EdgeLayout(src=n, dst=s)
                self._graph.add_edge(edge)

    def add_import_links(self) -> None:
        for n in self.file_nodes:
            module_ast = _parse_python_file(n)
            internal_imports, _ = get_module_imports(module_path=n, module_ast=module_ast, project_path=self.project_path)
            for int_imp in internal_imports:
                edge = pydot.Edge(
                    src=pydot.Node(n.as_posix()), 
                    dst=pydot.Node(int_imp.as_posix()),
                    color=ARGS.import_link_color,
                    style="dashed"
                )
                self._graph.add_edge(edge)

    def add_hightlight(self) -> None:
        n: pydot.Node
        for n in self._graph.get_node_list():
            print(n.get_name())
            n.set_style("filled")
            n.set_fillcolor("green")
        

def build_dot_layout(g: nx.DiGraph, 
                     project_path: Path, 
                     dir_as: str = "node",
                     show_interface: bool = False,
                     show_imports: bool = False
                     ) -> pydot.Dot:
    builder = GraphVizBuilder(path_graph=g, project_path=project_path)
    builder.add_file_nodes(with_interface=show_interface)

    if dir_as == "node":
        builder.add_dir_nodes()
        builder.add_hierarchy_links()
    elif dir_as == "cluster":
        builder.add_dir_clusters()
    else:
        raise ValueError(f"dir_as cannot take value: {dir_as}")
    
    if show_imports:
        builder.add_import_links()

    # builder.add_hightlight()

    return builder.graph

