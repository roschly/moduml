from pathlib import Path

import pydot
import astroid

from moduml_simple.core import main
from moduml_simple.module_imports import get_module_imports, ModuleImports


def test_module_imports():
    assert True

    import_cases = [
        "import numpy",
        "import numpy as np",
        "import numpy, astroid",
        "import astroid, numpy as np",
    ]

    import_from_cases = [
        "from numpy import array",
        "from .core import some_module",
        "from . import filtering",
    ]

    """ special cases:

    importing a folder --> should point to folder's __init__ file instead
    importing from within a package
    
    """

    """
    take module AST
    return simplified imports
    try to qualify imports
    
    """


"""
from package_one import module_one

options:
- root/package_one/module_one.py
- root/package_one.py
- root/package_one/__init__.py

"""


def test_get_module_imports():
    root = Path("foo")
    filepath = Path("foo/bar/mod.py")

    m = astroid.parse("import numpy as np")

    abs_imports = [
        ("import numpy", ["numpy"]),
        ("import numpy as np", ["numpy"]),
        ("import numpy, astroid", ["numpy", "astroid"]),
        ("import astroid, numpy as np", ["astroid", "numpy"]),
        #
        ("from numpy import array", ["numpy/array"]),
        #
        ("from baz import mod_two", ["baz/mod_two"]),
    ]

    for abs_imp in abs_imports:
        mod_imports: ModuleImports = get_module_imports(
            module=astroid.parse(abs_imp[0]), module_path=filepath, root=root
        )
        assert mod_imports.relative == []
        assert mod_imports.absolute == [root / a for a in abs_imp[1]]

    rel_imports = [
        ("from . import some_module", [filepath.parent / "some_module"]),
        ("from . import filtering", [filepath.parent / "filtering"]),
    ]

    for rel_imp in rel_imports:
        mod_imports: ModuleImports = get_module_imports(
            module=astroid.parse(rel_imp[0]), module_path=filepath, root=root
        )
        assert mod_imports.absolute == []
        assert mod_imports.relative == [a for a in rel_imp[1]], mod_imports.relative


def test_moduml_simple():

    # filepaths wrapped in extra layer of strings in order to match dot output
    modules = [
        '"test_dir/main.py";',
        '"test_dir/utils.py";',
        '"test_dir/package_one/__init__.py";',
        '"test_dir/package_one/module_one.py";',
        '"test_dir/package_one/module_two.py";',
        '"test_dir/package_two/__init__.py";',
        '"test_dir/package_two/module_one.py";',
    ]

    imports = [
        '"test_dir/main.py" -> "test_dir/utils.py";',
    ]

    root = Path("test_dir")

    dot: pydot.Dot = main(root=root)

    lines = dot.to_string().split("\n")
    for mod in modules:
        assert mod in lines, dot.to_string()

    # for imp in imports:
    #     assert imp in lines, dot.to_string()
