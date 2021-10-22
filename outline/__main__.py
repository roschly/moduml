from typing import Generator, List, Tuple
from pathlib import Path
from argparse import ArgumentParser, Namespace
import logging
import sys

import astroid
from xml.etree import ElementTree as ET

from .data_types import ModuleData
from .text_layouts import ModuleLayout as ModuleLayoutText
from .html_layouts import ModuleLayout as ModuleLayoutHtml

# name of txt file containing outline
# if to-txt flag enabled
DEFAULT_TXT_FILENAME = "_outline_"


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
        help=f"Save outline to '{DEFAULT_TXT_FILENAME}'.txt file.",
    )
    parser.add_argument(
        "--to-html",
        action="store_true",
        help=f"Save outline as HTML to '{DEFAULT_TXT_FILENAME}'.html file.",
    )
    return parser.parse_args()


def build_output_string(path_and_modules: List, absolute_path: bool, root: Path) -> str:
    s = ""
    for path, module in path_and_modules:
        # TODO: let ModuleLayout handle path string as well
        s += str(path) if absolute_path else str(path.relative_to(root))
        s += "\n" + str(ModuleLayoutText(ModuleData(module), n_indent=0))
    return s


def build_html_string(path_and_modules: List, absolute_path: bool, root: Path) -> str:
    # TODO: add css internal style
    html = ET.Element("html")
    head = ET.Element("head")
    html.append(head)

    style = ET.Element("style")
    style.text = """
    body {
            background-color: #1e1e1e; 
            color: white; 
            font-family: 
            monospace, monaco;
        }
    ul   {list-style-type: none;}
    
    .module_path {color: green;}
    .function_def {color: #03a1fc;}
    .function_return_type {color: #32cfc9; font-style: italic;}
    .class_def {color: #03a1fc;}
    .decorator {color: yellow;}
    .argument_type {color: #32cfc9; font-style: italic;}
    """
    head.append(style)

    body = ET.Element("body")
    html.append(body)

    for path, module in path_and_modules:
        mod = ModuleLayoutHtml(
            filepath=path if absolute_path else path.relative_to(root),
            module=ModuleData(module),
        )
        body.append(mod)

    return html


def main():
    """
    TODO:
        - data_types: output xml structure, then parse that into text (i.e. change indent-tag to spaces, etc)
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

    # TODO: don't traverse directory more than once?
    # filepaths to ignore
    paths_to_ignore = []
    if not args.include_test:
        paths_to_ignore += list(root.rglob("**/test_*.py"))
    if args.incl:
        # ignore all other filepaths than those found via incl glob pattern.
        paths_to_ignore += [
            f for f in filepaths if f not in list(root.rglob(args.incl))
        ]
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
            logging.warning(
                f"Ignoring file '{filepath}' because of the following error:"
            )
            logging.warning(e)

    # save as html
    if args.to_html:
        html = build_html_string(
            path_and_modules=path_and_modules,
            absolute_path=args.absolute_path,
            root=root,
        )
        ET.ElementTree(html).write(sys.stdout, encoding="unicode", method="html")
        return

    # save as text, either print to terminal or save to file
    s = build_output_string(
        path_and_modules=path_and_modules,
        absolute_path=args.absolute_path,
        root=root,
    )
    if args.to_txt:
        with open(DEFAULT_TXT_FILENAME + ".txt", "w") as fh:
            fh.write(s)
    else:
        print(s)


if __name__ == "__main__":
    main()
