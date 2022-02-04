from pathlib import Path

import astroid

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

    # TODO:
    # I need the case where there could be a conflict with names in __init__ and
    # names of modules in package
    # Example:
    #   package/mod01.py
    #       from . import bla
    #   if package/__init__.py contains a variable named bla, that would be imported
    #   if package/bla.py existed, moduml would assume it was imported, but it wouldnt if (see above)

    # TODO: should throw exception when trying to relative import beyond project structure
    # filepath = Path("foo/bar/mod.py")
    # ("from .....baz import func", [filepath.parents[1] / "baz/func"]),

    for (inputs, outputs) in inputs_outputs:
        m = astroid.parse(inputs)
        import_froms = relative_import_from(module=m, module_path=filepath)
        assert import_froms == [ImportFromPath(o) for o in outputs]

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
    pass
