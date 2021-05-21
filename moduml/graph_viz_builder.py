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
from .layout_types import DirLayout, FileLayout, EdgeLayout

# Global reference to program args, assigned from outside this module.
ARGS: argparse.Namespace = None




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
                                fontname="Helvetica",
                                concentrate=True # combine edges when possible
                                )
        self._graph.set_node_defaults(fontname="Helvetica")

    @property
    def graph(self) -> pydot.Dot:
        product = self._graph
        self.reset()
        return product

    def add_file_nodes(self, with_interface: bool = False) -> None:
        for n in self.file_nodes:
            node = FileLayout(node=n, 
                              with_interface=with_interface,
                              show_class_bases=ARGS.show_class_bases,
                              show_func_decorators=ARGS.show_func_decorators,
                              show_func_return_type=ARGS.show_func_return_type
                              )
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
    builder = GraphVizBuilder(path_graph=g, 
                              project_path=project_path,
                              rankdir=ARGS.rankdir
                              )
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

