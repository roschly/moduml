
from pathlib import Path
from typing import Dict, List, Tuple
import astroid
import itertools

import networkx as nx

from .module.imports import get_module_imports


def _parse_python_file(filepath: Path) -> astroid.Module:
    """ Parse a python file with astroid.
    """
    with open(filepath) as fh:
            code: str = fh.read()
    return astroid.parse(code)


class ModuleNetwork(nx.DiGraph):
    """
    """
    
    def __init__(self):
        super().__init__()

    def filter_nodes(self, node_type: str, data: bool = True) -> List[Tuple[Path, Dict]]:
        """
        """
        if data:
            return [(n,attr) for n,attr in self.nodes(data=True) if attr["_type"] == node_type]
        else:
            return [n for n,attr in self.nodes(data=True) if attr["_type"] == node_type]
    
    def filter_links(self, link_type: str) -> List[Tuple[Path, Path, Dict]]:
        """
        """
        return [(src,dst,attr) for src,dst,attr in self.edges(data=True) if attr["_type"] == link_type]
        

def filter_nodes(network: nx.DiGraph, node_type: str, data: bool = True) -> List[Tuple[Path, Dict]]:
    """
    """
    if data:
        return [(n,attr) for n,attr in network.nodes(data=True) if attr["_type"] == node_type]
    else:
        return [n for n,attr in network.nodes(data=True) if attr["_type"] == node_type]
    
def filter_links(network: nx.DiGraph, link_type: str) -> List[Tuple[Path, Path, Dict]]:
    """
    """
    return [(src,dst,attr) for src,dst,attr in network.edges(data=True) if attr["_type"] == link_type]


def create(filepaths: List[Path], project_path: Path) -> nx.DiGraph:
    """ Create a network/graph with file and dir nodes,
        with directory tree hierarchy links and module import links.
    """
    g = nx.DiGraph()
    # g = ModuleNetwork()

    # add hierarchy links
    # ex: dir -(hierarchy)-> dir/subdir
    for filepath in filepaths:
        g.add_edge(filepath.parent, filepath, _type="hierarchy")
        # add dir links, since filepaths only contain paths to files, not dirs
        if filepath.parent != project_path: # project_path is the root, so don't add link to it's parent
            g.add_edge(filepath.parents[1], filepath.parents[0], _type="hierarchy")
    
    # assign types to file/dir nodes
    filenodes: List[Path] = [n for n in g.nodes if n.suffix == ".py"]
    dirnodes: List[Path] = [n for n in g.nodes if not n.suffix]

    for fn in filenodes:
        g.nodes[fn]["_type"] = "file"

    for dn in dirnodes:
        g.nodes[dn]["_type"] = "dir"

    # add import links
    for filepath in filenodes:
        module_ast = _parse_python_file(filepath)
        internal_imports, external_imports = get_module_imports(module_path=filepath, 
                                                                module_ast=module_ast, 
                                                                project_path=project_path
                                                                )
        # add links to internal modules
        if internal_imports:
            edges_internal = itertools.product([filepath], internal_imports)
            g.add_edges_from(edges_internal, _type="import")

        # add external nodes, with external module type
        if external_imports:
            g.add_nodes_from(external_imports, _type="ext_package")
            
            # add links to external nodes
            edges_external = itertools.product([filepath], external_imports)
            g.add_edges_from(edges_external, _type="import")

    return g
