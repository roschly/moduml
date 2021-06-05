
from pathlib import Path
import astroid


def parse_python_file(filepath: Path) -> astroid.Module:
    """ Parse a python file with astroid.
    """
    with open(filepath) as fh:
            code: str = fh.read()
    return astroid.parse(code)
