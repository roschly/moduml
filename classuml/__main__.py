from pathlib import Path
from typing import List

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

    # [
    #     print(
    #         path.relative_to(root), ClassExtractor(filepath=path, module=module).classes
    #     )
    #     for path, module in path_and_modules
    # ]

    dot = pydot.Dot(
        graph_type="digraph", rankdir="LT", fontname="Helvetica", nodesep=2, ranksep=2
    )
    dot.set_node_defaults(fontname="Helvetica")
    for path, module in relative_paths_and_modules:
        parent_node = pydot.Node(name=path.parent.as_posix())
        dot.add_node(parent_node)
        path_node = pydot.Node(name=path.as_posix())
        dot.add_node(path_node)

        dot.add_edge(pydot.Edge(parent_node, path.as_posix()))

        cls_extractor = ClassExtractor(filepath=path, module=module)
        for cls in cls_extractor.classes:
            qualified_class_name = cls.name
            cls_node = pydot.Node(name=qualified_class_name)
            dot.add_node(cls_node)
            dot.add_edge(pydot.Edge(path_node, cls_node))

    # output as string or image file
    dot.write("bla.png", prog="dot", format="png")
    # print(dot.to_string())


if __name__ == "__main__":
    main()
