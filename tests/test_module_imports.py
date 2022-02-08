from pathlib import Path

import astroid
import pytest

from moduml.module.imports import (
    get_module_imports,
    relative_import_from,
    absolute_import_from,
    absolute_import,
    BaseImportPath,
    ImportFromPath,
    ImportPath,
)


def test_relative_import_from():
    filepath = Path("foo/bar/mod.py")

    # relative from ... import's
    inputs_outputs = [
        ("from . import array", [filepath.parent / "array"]),
        (
            "from . import array, matrix",
            [filepath.parent / elem for elem in ("array", "matrix")],
        ),
        ("from ..baz import func", [filepath.parents[1] / "baz/func"]),
        (
            "from ..baz import func as f, method as m",
            [filepath.parents[1] / elem for elem in ("baz/func", "baz/method")],
        ),
        (
            "from . import array\nfrom . import matrix",
            [filepath.parent / elem for elem in ("array", "matrix")],
        ),
    ]

    for (inputs, outputs) in inputs_outputs:
        m = astroid.parse(inputs)
        import_froms = relative_import_from(module=m, module_path=filepath)
        assert import_froms == [ImportFromPath(o) for o in outputs]

    # TODO:
    # I need the case where there could be a conflict with names in __init__ and
    # names of modules in package
    # Example:
    #   package/mod01.py
    #       from . import bla
    #   if package/__init__.py contains a variable named bla, that would be imported
    #   if package/bla.py existed, moduml would assume it was imported, but it wouldnt if (see above)

    # assert that a relative import beyong top-level results in no import
    # and program not throwing exception
    m = astroid.parse("from .....baz import func")
    import_froms = relative_import_from(module=m, module_path=filepath)
    import_froms = []

    # ensure it doesn't return anythin when given
    # non-relative imports
    m = astroid.parse("import numpy")
    import_froms = relative_import_from(module=m, module_path=filepath)
    assert import_froms == []

    m = astroid.parse("from numpy import array")
    import_froms = relative_import_from(module=m, module_path=filepath)
    assert import_froms == []


def test_absolute_import_from():
    root = Path("foo")

    inputs_outputs = [
        # we cant know the difference between
        # importing module from package and
        # importing function from module
        ("from package import module", [root / "package" / "module"]),
        ("from module import func", [root / "module" / "func"]),
        #
        (
            "from package import module01, module02",
            [root / "package" / "module01", root / "package" / "module02"],
        ),
        (
            "from package import module01 as mod1",
            [root / "package" / "module01"],
        ),
    ]

    for (inputs, outputs) in inputs_outputs:
        m = astroid.parse(inputs)
        import_froms = absolute_import_from(module=m, project_path=root)
        assert import_froms == [ImportFromPath(o) for o in outputs]

    # ensure return nothing when not absolute import froms
    m = astroid.parse("import package")
    import_froms = absolute_import_from(module=m, project_path=root)
    assert import_froms == []

    m = astroid.parse("from ..relative_package import module")
    import_froms = absolute_import_from(module=m, project_path=root)
    assert import_froms == []


def test_absolute_import():
    root = Path("foo")

    inputs_outputs = [
        ("import package", [root / "package"]),
        ("import package01, package02", [root / "package01", root / "package02"]),
        ("import package as pk, package02", [root / "package", root / "package02"]),
    ]

    for (inputs, outputs) in inputs_outputs:
        m = astroid.parse(inputs)
        import_froms = absolute_import(module=m, project_path=root)
        assert import_froms == [ImportFromPath(o) for o in outputs]

    # ensure return nothing when not absolute imports
    m = astroid.parse("from package import module")
    import_froms = absolute_import(module=m, project_path=root)
    assert import_froms == []

    m = astroid.parse("from ..relative_package import module")
    import_froms = absolute_import(module=m, project_path=root)
    assert import_froms == []


def test_try_to_qualify_import_path():
    import_path = Path("test_dir/package_one")
    path = BaseImportPath.try_to_qualify_import_path(import_path)
    assert path == import_path / "__init__.py"

    import_path = Path("test_dir/package_one/module_one")
    path = BaseImportPath.try_to_qualify_import_path(import_path)
    assert path == import_path.with_suffix(".py")

    import_path = Path("test_dir/utils")
    path = BaseImportPath.try_to_qualify_import_path(import_path)
    assert path == import_path.with_suffix(".py")

    import_path = Path("test_dir/package_three")
    path = BaseImportPath.try_to_qualify_import_path(import_path)
    assert not path


def test_import_path_try_to_qualify():
    pass


def test_import_from_path_try_to_qualify():
    # should work similar to its super class qualify method,
    # if path points to package or module
    import_path = Path("test_dir/package_one")
    assert (
        BaseImportPath.try_to_qualify_import_path(import_path)
        == ImportFromPath(import_path).try_to_qualify()
    )
    import_path = Path("test_dir/package_one/module_one")
    assert (
        BaseImportPath.try_to_qualify_import_path(import_path)
        == ImportFromPath(import_path).try_to_qualify()
    )

    # if path points to element in a module or package,
    # it should default to module or package/__init__
    import_path = Path("test_dir/package_one/module_one/function_one")
    assert ImportFromPath(import_path).try_to_qualify() == Path(
        "test_dir/package_one/module_one.py"
    )

    import_path = Path("test_dir/package_one/function_one")
    assert ImportFromPath(import_path).try_to_qualify() == Path(
        "test_dir/package_one/__init__.py"
    )

    # assert False


def test_get_module_imports():
    root = Path("test_dir")

    #
    # importing from a package; other packages and module in root
    #
    module_path = Path("test_dir/package_two/__init__.py")

    inputs_outputs = [
        ("from package_one import module_one", [root / "package_one/module_one.py"]),
        (
            "from package_one import non_existing_module",
            [root / "package_one/__init__.py"],
        ),  # default to package/__init__
        ("from ..package_one import module_one", [root / "package_one/module_one.py"]),
        ("from ..utils import util_function", [root / "utils.py"]),
        (
            "from ..package_one import module_one, module_two",
            [root / "package_one/module_one.py", root / "package_one/module_two.py"],
        ),
    ]

    for (inputs, outputs) in inputs_outputs:
        m = astroid.parse(inputs)
        internal_imports, external_imports = get_module_imports(
            module_path=module_path, module_ast=m, project_path=root
        )
        # TODO: maybe also test for reverse order, or as set, i.e. no order
        assert internal_imports == outputs or internal_imports == outputs[::-1]
        assert external_imports == []

    #
    # importing from a root module; other root module and from packages
    #
    module_path = Path("test_dir/main.py")

    inputs_outputs = [
        ("from package_one import module_one", [root / "package_one/module_one.py"]),
        (
            "from package_one import non_existing_module",
            [root / "package_one/__init__.py"],
        ),  # default to package/__init__
        ("from utils import util_function", [root / "utils.py"]),
    ]

    for (inputs, outputs) in inputs_outputs:
        m = astroid.parse(inputs)
        internal_imports, external_imports = get_module_imports(
            module_path=module_path, module_ast=m, project_path=root
        )
        assert internal_imports == outputs or internal_imports == outputs[::-1]
        assert external_imports == []

    #
    # importing external packages
    #
    module_path = Path("test_dir/main.py")

    inputs_outputs = [
        (
            "import ext_package",
            [Path("ext_package")],
        ),  # package does NOT exists locally, i.e. an external import
        # NOTE: this is probably not desired behavior in the long rung,
        # i.e. assuming relative unfound packages to be external ones
        (
            "from ..non_exisiting_package import module_one",
            [Path("non_exisiting_package")],
        ),
    ]

    for (inputs, outputs) in inputs_outputs:
        m = astroid.parse(inputs)
        internal_imports, external_imports = get_module_imports(
            module_path=module_path, module_ast=m, project_path=root
        )
        assert internal_imports == []
        assert external_imports == outputs

    # existing package should be internal not external import
    module_path = Path("test_dir/main.py")
    m = astroid.parse("import package_two")
    internal_imports, external_imports = get_module_imports(
        module_path=module_path, module_ast=m, project_path=root
    )
    assert internal_imports != []
    assert external_imports == []
