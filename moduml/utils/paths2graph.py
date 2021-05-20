""" Converts a set of Paths to a NetworkX graph
"""

from typing import Iterable, List, Tuple
from pathlib import Path, PureWindowsPath

import networkx as nx

# import streamlit as st

def _edges_from_path(path: Path) -> List[Tuple]:
    # path and parents
    # pp = ([path] + list(path.parents)[:-1])[::-1]
    pp = ([path] + list(path.parents))[::-1]
    edges = [(pp[i], pp[i+1]) for i in range(len(pp)-1)]
    return edges


def _add_edges_as_weighted(g, edges) -> None:
    for (src,dst) in edges:
        if g.has_edge(src, dst): 
            g[src][dst]["weight"] += 1
        else: 
            g.add_edge(src, dst, weight=1)


def to_graph(paths: Iterable[Path], is_windows_paths=False) -> nx.DiGraph:
    """
    """
    if is_windows_paths:
        paths = [PureWindowsPath(p) for p in paths]
    g = nx.DiGraph()

    all_edges = []
    for path in paths:
        edges = _edges_from_path(path)
        all_edges.extend(edges)
    _add_edges_as_weighted(g, all_edges)
    return g