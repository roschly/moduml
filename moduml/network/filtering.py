from pathlib import Path
from typing import Dict, List, Tuple
import astroid
import itertools

import networkx as nx


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