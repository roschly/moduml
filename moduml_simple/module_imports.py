from dataclasses import dataclass
from typing import List
from pathlib import Path

import astroid


@dataclass
class ModuleImports:
    relative: List[Path]
    absolute: List[Path]


def get_module_imports(
    module: astroid.Module, module_path: Path, root: Path
) -> ModuleImports:
    abs_imports = []
    rel_imports = []

    # import statements are always absolute
    import_statements = [e for e in module.body if isinstance(e, astroid.Import)]
    for imports in import_statements:
        names = [root / i[0] for i in imports.names]
        abs_imports += names

    # absolute import from
    import_from_statements = [
        e for e in module.body if isinstance(e, astroid.ImportFrom) and e.level is None
    ]

    # relative import from
    import_from_statements_with_level = [
        e for e in module.body if isinstance(e, astroid.ImportFrom) and e.level
    ]

    # absolute imports could be local imports
    # so keep X and Y in: from X import Y
    for import_froms in import_from_statements:
        for (name, alias) in import_froms.names:
            path = root / import_froms.modname / name
            abs_imports.append(path.with_suffix(""))

    # relative imports are always local
    # so keep X and Y in: from .X import Y
    for import_froms in import_from_statements_with_level:
        for (name, alias) in import_froms.names:
            relative_to = module_path.relative_to(
                module_path.parents[import_froms.level - 1]
            )
            path = root / relative_to / name
            rel_imports.append(path.with_suffix(""))

    return ModuleImports(
        relative=rel_imports,
        absolute=abs_imports,
    )
