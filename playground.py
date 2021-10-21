# %%

from pathlib import Path
import astroid

# %%

code = """
@some_decorator
class Bla(Blu):

    def __init__(self) -> None:
        pass

    def method_one(self, num: int) -> int:
        return num + 1

    def bla(self) -> pydot.Node:
        pass

@dataclass
@testing(a=1, b=2)
class Bli:
    name: str
    value: int

"""

module = astroid.parse(code)

# %%

cls_defs = [e for e in module.body if isinstance(e, astroid.ClassDef)]
cls_defs

c = cls_defs[0]
c


# %%

func_defs = list(c.mymethods())


# %%

f = func_defs[2]

# %%

# %%
