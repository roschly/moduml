from typing import List, Tuple
from pathlib import Path

import astroid

from .data_types import ModuleData
from .layouts import ModuleLayout


def main():
    """
    - create outline txt file with class, function and variable info


    """
    # create outline path if it doesnt exist
    outline_path = Path("outline.txt")
    with open(outline_path, "w") as fh:
        pass

    # loop through each py file in project root
    # root = Path.cwd() / "moduml"
    root = Path.cwd() / "example_code/latent-features"

    # TODO: this should remain a generator, not forced into a list
    filepaths: List[Path] = list(root.rglob("*.py"))
    path_and_modules: List[Tuple[Path, astroid.Module]] = []
    for filepath in filepaths:
        # TODO: handle errors
        with open(filepath) as fh:
            module = astroid.parse(fh.read())
        path_and_modules.append((filepath, module))

    # TODO: make use of relative paths an args flag
    relative_paths_and_modules = [
        (path.relative_to(root.parent), module) for path, module in path_and_modules
    ]

    with open(outline_path, "a") as fh:
        # for path, module in path_and_modules:
        for path, module in relative_paths_and_modules:
            s = (
                path.as_posix()
                + "\n"
                + str(ModuleLayout(ModuleData(module), n_indent=0))
            )

            fh.write(s)

    # TODO: make this optional via args flag
    with open(outline_path, "r") as fh:
        print(fh.read())


if __name__ == "__main__":
    # TODO:  add args
    # filter on: func return type, filepath, what to see (class, func, global vars)
    # show function/method arguments
    main()
