from argparse import Namespace, ArgumentParser, ArgumentTypeError
from pathlib import Path
from typing import Dict, List, Set

import pydot
import astroid

from .module_imports import get_module_imports
from .module_interface import get_module_interface, ModuleInterface


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("root", type=str, help="Project root")
    #
    parser.add_argument(
        "--dir-as",
        type=str,
        default="node",
        choices=["node", "cluster", "empty"],
        help="Draw a directory as 'node' (default), 'cluster' or 'empty' (not drawn).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Replace dot string output with name of image file incl. extension (e.g. img.png). Supports file formats from GraphViz (e.g. png, svg).",
    )
    parser.add_argument(
        "--excl",
        type=str,
        help="Glob pattern for excluding files. Exclude files matching the pattern and any links to them.",
    )
    # layout components
    parser.add_argument(
        "--full-filepath",
        action="store_true",
        help="Show filenames with their full path. Default is to only show filename.",
    )
    parser.add_argument(
        "--show-interface",
        action="store_true",
        help="Show interface (var + function names) on file nodes.",
    )
    parser.add_argument(
        "--show-imports", action="store_true", help="Show import links between files."
    )
    parser.add_argument(
        "--show-class-bases",
        action="store_true",
        help="Show the base classes for a class.",
    )
    parser.add_argument(
        "--show-func-return-type",
        action="store_true",
        help="Show the return type of a function.",
    )
    parser.add_argument(
        "--show-func-decorators",
        action="store_true",
        help="Show the decorators of a function.",
    )
    # styling
    parser.add_argument(
        "--rankdir",
        type=str,
        default="TB",
        choices=["TB", "LR"],
        help="Layout ordering for graph: 'TB' top-bottom (default), 'LR' left-right. OBS! 'LR' changes the interface layout.",
    )
    parser.add_argument(
        "--nodesep",
        type=float,
        default=0.5,
        help="Separation between nodes, i.e. horizontal spacing (when rankdir==top-bottom).",
    )
    parser.add_argument(
        "--ranksep",
        type=float,
        default=0.5,
        help="Separation between ranks (levels of nodes), i.e. vertical spacing (when rankdir==top-bottom).",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    # must be a directory path, for now
    root = Path(args.root)
    if not root.is_dir():
        raise ArgumentTypeError("Must be a directory path")

    # find all python files in path
    filepaths: List[Path] = list(root.rglob("*.py"))

    mod_to_imports: Dict[Path, List[Path]] = {}
    mod_to_interface: Dict[Path, ModuleInterface] = {}

    dot = pydot.Dot(
        graph_type="digraph",
        rankdir=args.rankdir,
        fontname="Helvetica",
        nodesep=args.nodesep,
        ranksep=args.ranksep,
    )

    for filepath in filepaths:
        try:
            print(filepath)
            with open(filepath) as fh:
                code: str = fh.read()
            m = astroid.parse(code)

            mod_to_interface[filepath] = get_module_interface(m)
            mod_to_imports[filepath] = get_module_imports(
                module=m, module_path=filepath, root=root
            )

            print(mod_to_imports[filepath])

            dot.add_node(pydot.Node(name=filepath.as_posix()))

        except Exception as e:
            print(f"Error when processing: {filepath}")
            print(e)

    # for mod in mod_to_imports.keys():
    #     imps = mod_to_imports[mod]
    #     if len(imps.relative) > 0:
    #         dst = imps.relative[0]
    #     edge = pydot.Edge(src=mod.as_posix(), dst=dst.as_posix())
    #     dot.add_edge(edge)

    # output as string or image file
    if args.output_file:
        file_ext = args.output_file.split(".")[-1]
        dot.write(args.output_file, prog="dot", format=file_ext)
    else:
        print(dot.to_string())
