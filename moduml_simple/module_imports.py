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

    import_statements = [e for e in module.body if isinstance(e, astroid.Import)]
    for imports in import_statements:
        names = [root / i[0] for i in imports.names]
        abs_imports += names

    import_from_statements = [
        e for e in module.body if isinstance(e, astroid.ImportFrom)
    ]

    for import_froms in import_from_statements:
        if import_froms.level is None:  # if no relative level, abs import
            abs_imports.append(root / import_froms.modname)
        else:
            relative_to = module_path.relative_to(
                module_path.parents[import_froms.level - 1]
            )
            print(module_path.parents[import_froms.level - 1])
            print(relative_to)
            rel_imports.append(root / relative_to)

    return ModuleImports(
        relative=rel_imports,
        absolute=abs_imports,
    )
