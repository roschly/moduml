from typing import List, Tuple

from .data_types import ArgumentData, ModuleData, ClassData, FunctionData


# Define tab as 4 spaces
TAB = " " * 4


class DecoratorsLayout:
    def __init__(self, decorators: List[str], n_indent: int) -> None:
        self.decorators = decorators
        self.n_indent = n_indent

    def __repr__(self) -> str:
        s = ""
        if self.decorators:
            for deco in self.decorators:
                s += f"{TAB*self.n_indent}" + "@" + deco + "\n"
        return s


class ArgumentsLayout:
    def __init__(self, arguments: List[ArgumentData], n_indent: int) -> None:
        self.arguments = arguments
        self.n_indent = n_indent

    def __str__(self) -> str:
        s = ""

        # keep args in one line if not too many,
        # else split into separate lines
        # TODO: make this dependent on line length, not num args?
        if len(self.arguments) <= 3:
            s += "(" + ", ".join([str(a) for a in self.arguments]) + ")"
        else:
            s += "(" + "\n"
            for arg in self.arguments:
                s += f"{TAB*self.n_indent}" + str(arg) + "\n"
            s += f"{TAB*self.n_indent}" + ")"

        return s


class FunctionLayout:
    def __init__(self, func_data: FunctionData, n_indent: int) -> None:
        self.func_data = func_data
        self.n_indent = n_indent

    def __str__(self) -> str:
        return_type_str = (
            " -> " + self.func_data.return_type if self.func_data.return_type else ""
        )
        arguments_str = str(
            ArgumentsLayout(self.func_data.arguments, n_indent=self.n_indent + 1)
        )
        decorators_str = str(
            DecoratorsLayout(self.func_data.decorators, n_indent=self.n_indent)
        )

        s = (
            decorators_str
            + f"{TAB*self.n_indent}"
            + "def "
            + self.func_data.name
            + arguments_str
            + return_type_str
            + "\n"
        )
        return s


class ClassLayout:
    def __init__(self, class_data: ClassData, n_indent: int) -> None:
        self.class_data = class_data
        self.n_indent = n_indent

    def __str__(self) -> str:
        # TODO: add decotators
        # TODO: add self.vars defined in init?
        # TODO: handle line break if too many base names
        basenames_str = (
            ""
            if not self.class_data.basenames
            else "(" + ", ".join(self.class_data.basenames) + ")"
        )
        decorators_str = str(
            DecoratorsLayout(self.class_data.decorators, n_indent=self.n_indent)
        )

        s = (
            decorators_str
            + f"{TAB*self.n_indent}"
            + "class "
            + self.class_data.name
            + basenames_str
            + "\n"
        )
        method: FunctionData
        for method in self.class_data.methods:
            s += str(FunctionLayout(method, n_indent=self.n_indent + 1))
        return s


class ModuleLayout:
    def __init__(self, module: ModuleData, n_indent: int) -> None:
        self.module = module
        self.n_indent = n_indent

    def __str__(self) -> str:
        s = ""
        for cls in self.module.classes:
            s += (
                f"{TAB*self.n_indent}"
                + str(ClassLayout(cls, n_indent=self.n_indent + 1))
                + "\n"
            )
        return s
