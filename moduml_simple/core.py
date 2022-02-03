from argparse import Namespace, ArgumentParser, ArgumentTypeError
from pathlib import Path
from typing import Dict, List, Set

import pydot
import astroid

from .module_imports import get_module_imports
from .module_interface import get_module_interface, ModuleInterface


def main(
    root: Path,
    rankdir: str = "TB",
    ranksep: float = 0.5,
    nodesep: float = 0.5,
    output_file: str = None,
    **kwargs,
) -> pydot.Dot:

    # must be a directory path, for now
    if not root.is_dir():
        raise ArgumentTypeError("Must be a directory path")

    # find all python files in path
    filepaths: List[Path] = list(root.rglob("*.py"))

    mod_to_imports: Dict[Path, List[Path]] = {}
    mod_to_interface: Dict[Path, ModuleInterface] = {}

    dot = pydot.Dot(
        graph_type="digraph",
        rankdir=rankdir,
        fontname="Helvetica",
        nodesep=nodesep,
        ranksep=ranksep,
    )

    for filepath in filepaths:
        try:
            with open(filepath) as fh:
                code: str = fh.read()
            m = astroid.parse(code)

            mod_to_interface[filepath] = get_module_interface(m)
            mod_to_imports[filepath] = get_module_imports(
                module=m, module_path=filepath, root=root
            )

            dot.add_node(pydot.Node(name=filepath.as_posix()))

        except Exception as e:
            print(f"Error when processing: {filepath}")
            print(e)

    for mod in mod_to_imports.keys():
        imps = mod_to_imports[mod]
        for rel_imp in imps.relative:
            edge = pydot.Edge(src=mod.as_posix(), dst=rel_imp.as_posix())
            dot.add_edge(edge)

    return dot
