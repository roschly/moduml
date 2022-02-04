from pathlib import Path
from typing import Dict, List, Tuple
import astroid
import itertools

import networkx as nx

from ..module.imports import get_module_imports
from . import utils


def create(filepaths: List[Path], project_path: Path) -> nx.DiGraph:
    """Create a network/graph with file and dir nodes,
    with directory tree hierarchy links and module import links.
    """
    g = nx.DiGraph()

    # add hierarchy links
    # ex: dir -(hierarchy)-> dir/subdir
    for filepath in filepaths:
        g.add_edge(filepath.parent, filepath, _type="hierarchy")
        # add dir links, since filepaths only contain paths to files, not dirs
        if filepath.parent != project_path:
            # project_path is the root, so don't add link to it's parent
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
        module_ast = utils.parse_python_file(filepath)
        internal_imports, external_imports = get_module_imports(
            module_path=filepath,
            module_ast=module_ast,
            project_path=project_path,
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
