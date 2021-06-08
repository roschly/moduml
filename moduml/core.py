
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import List, Set
import logging

import pydot
import networkx as nx

from . import graph_viz_builder
from . import network


def exclude_nodes(project_path: Path,
                  net: nx.DiGraph,
                  excl_pattern: str, 
                  incl_pattern: str
                  ) -> Set[Path]:
    """ Returns the nodes/filepaths to be excluded, based on excl and incl patterns.
        Excl: exclude any node that matches the excl pattern
        Incl: exclude any node that isnt in the incl pattern OR shares an edge with one.
    """
    incl_filepaths = []
    excl_filepaths = []
    if incl_pattern:
        incl_filepaths: List[Path] = list(project_path.rglob(incl_pattern))
    if excl_pattern:
        excl_filepaths: List[Path] = list(project_path.rglob(excl_pattern))

    # excl files
    excl_nodes = [n for n,attr in net.nodes(data=True) if n in excl_filepaths and attr["_type"] == "file"]

    # incl files
    if incl_pattern:
        incl_edges = [(src,dst) for src,dst in net.edges() if src in incl_filepaths or dst in incl_filepaths]
        incl_net = nx.DiGraph()
        incl_net.add_edges_from(incl_edges)
        excl_nodes += [n for n,attr in net.nodes(data=True) if n not in incl_net.nodes() and attr["_type"] == "file"]
    
    # Return nodes without duplicates (e.g. set)
    return set(excl_nodes)
    

def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("path", type=str, help="Path to directory containing python project.")
    #
    parser.add_argument("--dir-as", type=str, default="node", choices=["node", "cluster", "empty"], help="Draw a directory as 'node' (default), 'cluster' or 'empty' (not drawn).")
    parser.add_argument("--output-file", type=str, help="Replace dot string output with name of image file incl. extension (e.g. img.png). Supports file formats from GraphViz (e.g. png, svg).")
    parser.add_argument("--excl", type=str, help="Glob pattern for excluding files. Exclude files matching the pattern and any links to them.")
    parser.add_argument("--incl", type=str, help="Glob pattern for including files. Only files matching incl pattern AND files they import are shown.")
    parser.add_argument("--highlight", type=str, default=None, help="Name of EXTERNAL package. Files that import it will be highlighted via color.")
    # layout components
    parser.add_argument("--full-filepath", action="store_true", help="Show filenames with their full path. Default is to only show filename.")
    parser.add_argument("--show-interface", action="store_true", help="Show interface (var + function names) on file nodes.")
    parser.add_argument("--show-imports", action="store_true", help="Show import links between files.")
    parser.add_argument("--ignore-imports", action="store_true", help="Import links won't affect graph layout.")
    parser.add_argument("--show-class-bases", action="store_true", help="Show the base classes for a class.")
    parser.add_argument("--show-func-return-type", action="store_true", help="Show the return type of a function.")
    parser.add_argument("--show-func-decorators", action="store_true", help="Show the decorators of a function.")
    # styling
    parser.add_argument("--rankdir", type=str, default="TB", choices=["TB", "LR"], help="Layout ordering for graph: 'TB' top-bottom (default), 'LR' left-right. OBS! 'LR' changes the interface layout.")
    parser.add_argument("--nodesep", type=float, default=0.5, help="Separation between nodes, i.e. horizontal spacing (when rankdir==top-bottom).")
    parser.add_argument("--ranksep", type=float, default=0.5, help="Separation between ranks (levels of nodes), i.e. vertical spacing (when rankdir==top-bottom).")
    parser.add_argument("--combine-links", action="store_true", help="Combine links when possible, to minimize the clutter. OBS: combines edges of different types.")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    
    # must be a directory path, for now
    path = Path(args.path)
    if not path.is_dir():
        raise argparse.ArgumentTypeError("Must be a directory path")

    # find all python files in path
    filepaths: List[Path] = list(path.rglob("*.py"))

    # convert filepaths to graph
    net: nx.DiGraph = network.create(filepaths, project_path=path)

    # check that external package for highlighting exists
    if args.highlight:
        ext_package = Path(args.highlight)
        if ext_package in net.nodes() and net.nodes[ext_package]["_type"] == "ext_package": 
            pass
        else: 
            args.highlight = None
            logging.warning(f"Cannot find external package to highlight: '{ext_package}'")
    
    # exclude nodes based on glob pattern args
    excl_nodes = exclude_nodes(project_path=path, net=net, excl_pattern=args.excl, incl_pattern=args.incl)
    net.remove_nodes_from(excl_nodes)
    
    # Make args available to the graph_viz_builder module.
    # Purpose: easy access to styling options, e.g. import-link-color.
    # Otherwise all these options would have to be pipped all the way down.
    graph_viz_builder.ARGS = args

    # create directory view
    dot: pydot.Dot = graph_viz_builder.build_dot_layout(network=net, 
                                                    project_path=path,
                                                    dir_as=args.dir_as, 
                                                    show_interface=args.show_interface,
                                                    show_imports=args.show_imports
                                                    )
    
    # output as string or image file
    if args.output_file:
        file_ext = args.output_file.split(".")[-1]
        dot.write(args.output_file, prog="dot", format=file_ext)
    else:
        print(dot.to_string())

