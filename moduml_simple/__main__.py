from argparse import Namespace, ArgumentParser

import pydot

from .core import main


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


if __name__ == "__main__":
    args = parse_args()
    dot: pydot.Dot = main(vars(args))

    if args.output_file:
        file_ext = args.output_file.split(".")[-1]
        dot.write(args.output_file, prog="dot", format=file_ext)
    else:
        print(dot.to_string())
