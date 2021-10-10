from pathlib import Path
from typing import Dict, List, Tuple

import astroid
import pydot


class ClassExtractor:
    """Extracts classes from a module."""

    def __init__(self, filepath: Path, module: astroid.Module) -> None:
        self.filepath = filepath
        self.module = module

        self.classes = []

        self._extract_classes()

    def _extract_classes(self) -> None:
        self.classes = [e for e in self.module.body if isinstance(e, astroid.ClassDef)]


def main():
    """
    - get project root dir
    - find all .py files
    - zip filepath with astroid module
    - get classes with info associated with each filepath
    - create dot graph from these classes
    """
    root = Path.cwd() / "moduml"

    # TODO: this should remain a generator, not forced into a list
    filepaths: List[Path] = list(root.rglob("*.py"))
    path_and_modules = []
    for filepath in filepaths:
        # TODO: handle errors
        with open(filepath) as fh:
            module = astroid.parse(fh.read())
        path_and_modules.append((filepath, module))

    relative_paths_and_modules = [
        (path.relative_to(root.parent), module) for path, module in path_and_modules
    ]

    dot = pydot.Dot(
        graph_type="digraph", rankdir="LR", fontname="Helvetica", nodesep=1, ranksep=1
    )
    dot.set_node_defaults(fontname="Helvetica")

    # handle nodes and edges in dicts, to avoid pydots double quoting "" of node names
    # which makes it very difficult to locate the proper node from path (via pydot)
    nodes: Dict[Path, pydot.Node] = {}
    edges: Dict[Tuple[Path, Path], pydot.Edge] = {}

    # add root as first node
    nodes[root.relative_to(root.parent)] = pydot.Node(name=root.stem)

    # add all files and folders as nodes
    for filepath, _ in relative_paths_and_modules:
        path = filepath
        for i in range(len(filepath.parts) - 1):
            if not path in nodes:
                nodes[path] = pydot.Node(name=path.as_posix())
            path = path.parent

    # add directory hierarchy between folders and files, as edges
    for filepath, _ in relative_paths_and_modules:
        path = filepath
        for i in range(len(filepath.parts) - 1):
            parent = path.parent
            edge = pydot.Edge(nodes[parent], nodes[path])
            if not (parent, path) in edges:
                edges[(parent, path)] = edge
            path = parent

    # if _is_package(network=network, node=node): self.set("shape", "component")
    #     else: self.set("shape", "folder")
    #     self.set("color", "red")

    # add nodes to pydot graph
    for path, node in nodes.items():
        shape = "folder" if path.is_dir() else "component"
        node.set("shape", shape)
        dot.add_node(node)

    # add edges to pydot graph
    for _, edge in edges.items():
        dot.add_edge(edge)

    # add edge from file/module to class
    for path, module in relative_paths_and_modules:
        cls_extractor = ClassExtractor(filepath=path, module=module)
        for cls in cls_extractor.classes:
            qualified_class_name = cls.name
            path_node = nodes[path]
            cls_node = pydot.Node(name=qualified_class_name)
            cls_node.set("shape", "rect")
            dot.add_node(cls_node)
            dot.add_edge(pydot.Edge(path_node, cls_node))

    # output as string or image file
    dot.write("bla.png", prog="dot", format="png")
    print(dot.to_string())


if __name__ == "__main__":
    main()
