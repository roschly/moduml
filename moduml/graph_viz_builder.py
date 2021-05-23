from typing import Dict, List, Tuple
from pathlib import Path
import argparse
import re

import networkx as nx
import pydot
import astroid

from .module.imports import get_module_imports
from .layout_types import DirLayout, FileLayout, EdgeLayout
from .network_creator import ModuleNetwork


# Global reference to program args, assigned from outside this module.
ARGS: argparse.Namespace = None



def _handle_weird_pydot_name(cluster_node: Path) -> str:
    """ pydot.Node names appear to be wrapped in an extra layer of strings
            e.g. "dir1/file1.py" --> '"dir1/file1.py"'
        So, pass string through Node constructor and retrieve name, in order to replicate.
    """
    cluster_node_name = pydot.Node(name=cluster_node.as_posix()).get_name()
    return cluster_node_name


class GraphVizBuilder:
    def __init__(self, 
                 network: ModuleNetwork, 
                 project_path: Path, 
                 rankdir: str = "TB"
                 ) -> None:
        self.rankdir = rankdir
        self.network: ModuleNetwork = network
        self.project_path = project_path

        self.file_nodes = network.filter_nodes("file", data=False)
        self.dir_nodes = network.filter_nodes("dir", data=False)
        self.internal_import_links =\
            [(src,dst) for src,dst,_ in self.network.filter_links("import") if src in self.file_nodes and dst in self.file_nodes]
        self.hierarchy_links = self.network.filter_links("hierarchy")

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
                              full_filepath=ARGS.full_filepath,
                              show_class_bases=ARGS.show_class_bases,
                              show_func_decorators=ARGS.show_func_decorators,
                              show_func_return_type=ARGS.show_func_return_type
                              )
            self._graph.add_node(node)

    def add_dir_nodes(self) -> None:
        for n in self.dir_nodes:
            node = DirLayout(network=self.network, node=n)
            self._graph.add_node(node)

    def add_dir_clusters(self) -> None:
        for n in self.dir_nodes:
            c = pydot.Cluster(n.as_posix(), 
                            #  label=n.relative_to(n.parent).as_posix(), 
                             label=n.as_posix(),
                             color="gray")
            # add nodes to cluster
            cluster_nodes =\
                [dst for src,dst,_ in self.hierarchy_links if src==n and self.network.nodes[dst]["_type"] == "file"]

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
        for src,dst,_ in self.hierarchy_links:
            edge = EdgeLayout(src=src, dst=dst, color="gray", style="solid")
            self._graph.add_edge(edge)


    def add_import_links(self) -> None:
        for src,dst in self.internal_import_links:
            edge = EdgeLayout(src=src, 
                              dst=dst, 
                              color="black", 
                              style="dashed", 
                              constraint=(not ARGS.ignore_imports)
                              )
            self._graph.add_edge(edge)


def build_dot_layout(network: nx.DiGraph, 
                     project_path: Path, 
                     dir_as: str = "node",
                     show_interface: bool = False,
                     show_imports: bool = False
                     ) -> pydot.Dot:
    builder = GraphVizBuilder(network=network, 
                              project_path=project_path,
                              rankdir=ARGS.rankdir
                              )
    builder.add_file_nodes(with_interface=show_interface)

    if dir_as == "node":
        builder.add_dir_nodes()
        builder.add_hierarchy_links()
    elif dir_as == "cluster":
        builder.add_dir_clusters()
    elif dir_as == "empty":
        pass
    else:
        raise ValueError(f"dir_as cannot take value: {dir_as}")
    
    if show_imports:
        builder.add_import_links()

    return builder.graph
