import pathlib
from pathlib import Path, PurePath
from typing import Any, List, Dict, Optional, Tuple, Union
from functools import singledispatch

import astroid
import networkx as nx


class BaseImportPath:
    def __init__(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            self.path = Path(path)
        else:
            self.path = path
        assert (
            not self.path.suffix
        ), "An import path should not point to a specific file."

    def __getattr__(self, name: str) -> Any:
        return getattr(self.path, name)

    def __str__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return str(self.path)

    def __truediv__(self, key):
        return self.path.__truediv__(key)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, BaseImportPath):
            return self.path == other.path
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def try_to_qualify(self):
        raise NotImplementedError

    @staticmethod
    def try_to_qualify_import_path(import_path: Path) -> Optional[Path]:
        # imports a module, if it points to a .py file with same name
        module_import = Path(str(import_path) + ".py")
        if module_import.exists():
            return module_import

        # imports a package, if it points to a dir with an __init__.py file
        package_import = import_path / "__init__.py"
        if package_import.exists():
            return package_import

        # could not be qualified / linked to a specific .py file
        return None


class ImportPath(BaseImportPath):
    def __init__(self, path) -> None:
        super().__init__(path)

    def try_to_qualify(self) -> Optional[Path]:
        """Import can import: module or package, but not element in either.
        Examples:
            package/module --> package/module.py
            package --> package/__init__.py
        """
        # qual_import = BaseImportPath.try_to_qualify_import_path(self.path)
        # if qual_import and qual_import.suffix == ".py":
        #     return qual_import
        # return None

        return BaseImportPath.try_to_qualify_import_path(self.path)


class ImportFromPath(BaseImportPath):
    def __init__(self, path) -> None:
        super().__init__(path)

    def try_to_qualify(self) -> Optional[Path]:
        """ImportFrom can import: package, module or element in package or module
        Examples:
            package/module/func --> package/module.py
            package/module --> package/module.py
            package --> package/__init__.py
        """
        # if imports a module or package
        # qual_import = BaseImportPath.try_to_qualify_import_path(self.path)
        # if qual_import and qual_import.suffix == ".py":
        #     return qual_import
        qual_import = BaseImportPath.try_to_qualify_import_path(self.path)
        if qual_import:
            return qual_import

        # if imports an element in a module or package
        # try to qualify import path parent
        qual_import = BaseImportPath.try_to_qualify_import_path(self.path.parent)
        if qual_import and qual_import.suffix == ".py":
            return qual_import
        # import from path could not be qualified
        return None


def _to_rel_importfrom_paths(
    import_from: astroid.ImportFrom,
    module_path: Path,
) -> List[ImportFromPath]:
    """Convert ImportFrom statement to import paths relative to module path.
    Ex:
        import_from: from ..modname import name1 as n1, name2
        module_path: dir1/dir2/module.py
        --> dir1/modname
        --> dir1/modname/name1 (alias ignored)
            dir1/modname/name2
    """
    assert import_from.level, "level must be present for a relative import"
    p = module_path.parents[import_from.level - 1] / import_from.modname.replace(
        ".", "/"
    )
    return [ImportFromPath(p / n[0]) for n in import_from.names]


def _to_abs_importfrom_paths(
    import_from: astroid.ImportFrom,
    project_path: Path,
) -> List[ImportFromPath]:
    assert not import_from.level, "level must NOT be present for an absolute import"
    path_strs = [
        (import_from.modname + "." + name).replace(".", "/")
        for name, alias in import_from.names
    ]
    return [ImportFromPath(project_path / Path(p)) for p in path_strs]


def _to_abs_import_paths(
    abs_import: astroid.Import,
    project_path: Path,
) -> List[ImportPath]:
    return [
        ImportPath(project_path / name.replace(".", "/"))
        for name, alias in abs_import.names
    ]


def relative_import_from(
    module: astroid.Module,
    module_path: Path,
) -> List[ImportFromPath]:
    """Returns the relative ImportFrom's of the module.
    Ex: relative ImportFrom
        from .mod1 import func1, func2
        from . import mod1, mod2
    """
    rel_import_froms = [
        e for e in module.body if isinstance(e, astroid.ImportFrom) and e.level
    ]

    import_paths: List[ImportPath] = []
    for import_from in rel_import_froms:
        import_paths.extend(_to_rel_importfrom_paths(import_from, module_path))
    return import_paths


def absolute_import_from(
    module: astroid.Module,
    project_path: Path,
) -> List[ImportFromPath]:
    """Returns the absolute ImportFrom's of the module.
    Ex: absolute ImportFrom
        from package1.mod import class, func
        from package1 import mod1 as m1, mod2
    """
    abs_import_froms = [
        e for e in module.body if isinstance(e, astroid.ImportFrom) and not e.level
    ]

    import_paths = []
    for imp in abs_import_froms:
        import_paths.extend(
            _to_abs_importfrom_paths(import_from=imp, project_path=project_path)
        )
    return import_paths


def absolute_import(module: astroid.Module, project_path: Path) -> List[ImportPath]:
    """Returns the absolute Import of the module.
    Ex: absolute Import
        import mod
    """
    imports = [e for e in module.body if isinstance(e, astroid.Import)]

    import_paths = []
    for imp in imports:
        import_paths.extend(
            _to_abs_import_paths(abs_import=imp, project_path=project_path)
        )
    return import_paths


def qualify_import_paths(
    import_paths: List[BaseImportPath],
) -> Tuple[List[Path], List[BaseImportPath]]:
    qual_paths = []
    non_qual_paths = []
    for p in import_paths:
        maybe_qual = p.try_to_qualify()
        if maybe_qual:
            qual_paths.append(maybe_qual)
        else:
            non_qual_paths.append(p)
    return qual_paths, non_qual_paths


def is_dir(graph: nx.DiGraph, node: Path) -> bool:
    return len(list(graph.successors(node))) > 0


def get_module_imports(
    module_path: Path,
    module_ast: astroid.Module,
    project_path: Path,
) -> Tuple[List[Path], List[Path]]:
    # --- ImportFrom
    # Import paths that do NOT point to specific python files
    rel_import_from: List[Path] = relative_import_from(
        module=module_ast, module_path=module_path
    )
    abs_import_from: List[Path] = absolute_import_from(
        module=module_ast, project_path=project_path
    )
    # --- Import
    abs_import: List[Path] = absolute_import(
        module=module_ast, project_path=project_path
    )

    all_import_paths = abs_import + abs_import_from + rel_import_from
    qual_import_paths, non_qual_import_paths = qualify_import_paths(
        import_paths=all_import_paths
    )

    for p in qual_import_paths:
        assert p.suffix == ".py", "all qualified paths must point to a .py file"

    for p in non_qual_import_paths:
        assert not p.suffix, "all non-qualifed paths must not point to a specific file"

    # only show top-level package name for external imports
    # e.g. "from sklearn.mixtures import GMM" --> sklearn
    ext_toplevel_imports = [
        Path(ext.relative_to(project_path).parts[0]) for ext in non_qual_import_paths
    ]

    # remove duplicates
    internal_imports = qual_import_paths
    return list(set(internal_imports)), list(set(ext_toplevel_imports))
