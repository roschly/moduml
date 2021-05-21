
import argparse
from pathlib import Path
from typing import List

import pydot
import networkx as nx

from . import graph_viz_builder
from .utils import paths2graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to directory containing python project.")
    #
    parser.add_argument("--dir-as", type=str, default="node", help="Draw a directory as 'node' (default) or 'cluster'.")
    parser.add_argument("--output-file", type=str, help="Replace dot string output with name of image file incl. extension (e.g. img.png). Supports file formats from GraphViz (e.g. png, svg).")
    parser.add_argument("--ignore-files", type=str, help="Glob pattern for ignoring files.")
    # layout components
    parser.add_argument("--show-interface", action="store_true", help="Show interface (var + function names) on file nodes.")
    parser.add_argument("--show-imports", action="store_true", help="Show import links between files.")
    parser.add_argument("--show-class-bases", action="store_true", help="Show the base classes for a class.")
    parser.add_argument("--show-func-return-type", action="store_true", help="Show the return type of a function.")
    parser.add_argument("--show-func-decorators", action="store_true", help="Show the decorators of a function.")
    # styling
    parser.add_argument("--rankdir", type=str, default="TB", help="Layout ordering for graph: 'TB' top-bottom (default), 'LR' left-right. OBS! 'LR' changes the interface layout.")
    parser.add_argument("--import-link-color", type=str, default="black", help="Color of import link, e.g. 'black', 'gray', 'royalblue'. See options: https://www.graphviz.org/doc/info/colors.html")
    args = parser.parse_args()

    # Make args available to the graph_viz_builder module.
    # Purpose: easy access to styling options, e.g. import-link-color.
    # Otherwise all these options would have to be pipped all the way down.
    graph_viz_builder.ARGS = args

    # must be a directory path, for now
    path = Path(args.path)
    if not path.is_dir():
        raise argparse.ArgumentTypeError("Must be a directory path")
    
    # find all python files in path
    filepaths: List[Path] = list(path.rglob("*.py"))

    # optional: ignore files pattern
    ignore_filepaths = []
    if args.ignore_files:
        ignore_filepaths: List[Path] = list(path.rglob(args.ignore_files))
    filepaths = [p for p in filepaths if p not in ignore_filepaths]

    # convert filepaths to graph
    graph: nx.DiGraph = paths2graph.to_graph(paths=filepaths)

    # create directory view
    dot: pydot.Dot = graph_viz_builder.build_dot_layout(g=graph, 
                                                    project_path=path,
                                                    dir_as=args.dir_as, 
                                                    show_interface=args.show_interface,
                                                    show_imports=args.show_imports
                                                    )
    
    # output as string or PNG file
    if args.output_file:
        file_ext = args.output_file.split(".")[-1]
        dot.write(args.output_file, prog="dot", format=file_ext)
    else:
        print(dot.to_string())

