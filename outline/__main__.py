from typing import Generator, List, Tuple
from pathlib import Path
from argparse import ArgumentParser, Namespace
import logging

import astroid

from .data_types import ModuleData
from .layouts import ModuleLayout

# name of txt file containing outline
# if to-txt flag enabled
DEFAULT_TXT_FILENAME = "_outline_.txt"


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("dir", type=str, help="root directory path of project.")
    parser.add_argument(
        "--include-test",
        action="store_true",
        help="include '**/test_*.py' files in outline.",
    )
    parser.add_argument(
        "--incl",
        type=str,
        help="""only include filepaths that match INCL glob pattern. 
        E.g. '**/dirA/*.py' only include .py files in any directory called 'dirA'.""",
    )
    parser.add_argument(
        "--absolute-path",
        action="store_true",
        help="use absolute (instead of relative) path of each .py file.",
    )
    parser.add_argument(
        "--to-txt",
        action="store_true",
        help=f"Save outline to '{DEFAULT_TXT_FILENAME}' file.",
    )
    return parser.parse_args()


def main():
    """
    TODO:
        - add default values to args?
        - consider custom file ext and color scheme for that ext in vscode
        - filter on: func return type, what to see (class, func, global vars)
        - show function/method arguments
    """

    args: Namespace = parse_args()

    root = Path.cwd() / Path(args.dir)
    if not root.is_dir():
        raise Exception("'dir' must be an existing directory.")

    # find all .py filepaths in root
    filepaths: List[Path] = list(root.rglob("*.py"))
    print(len(filepaths))

    # TODO: don't traverse directory more than once?
    # filepaths to ignore
    paths_to_ignore = []
    if not args.include_test:
        paths_to_ignore += root.rglob("**/test_*.py")
    if args.incl:
        # ignore all other filepaths than those found via incl glob pattern.
        paths_to_ignore += [f for f in filepaths if f not in root.rglob(args.incl)]
        if len(paths_to_ignore) == len(filepaths):
            logging.warning(
                f"All filepaths are being ignored with the current INCL glob pattern: {args.incl}"
            )

    # combine each python module with its Abstract Syntax Tree
    path_and_modules: List[Tuple[Path, astroid.Module]] = []
    for filepath in [f for f in filepaths if f not in paths_to_ignore]:
        try:
            with open(filepath) as fh:
                module = astroid.parse(fh.read())
            path_and_modules.append((filepath, module))
        except Exception as e:
            logging.warning(f"Ignoring file '{filepath}' because of the following error:")
            logging.warning(e)

    # build output string
    s = ""
    for path, module in path_and_modules:
        s += str(path) if args.absolute_path else str(path.relative_to(root))
        s += "\n" + str(ModuleLayout(ModuleData(module), n_indent=0))

    # save or print output
    if args.to_txt:
        with open(DEFAULT_TXT_FILENAME, "w") as fh:
            fh.write(s)
    else:
        print(s)


if __name__ == "__main__":
    main()
