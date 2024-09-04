import sys

from ..code import py_module


def _init_mod() -> None:
    print("_init_mod()")
    code = py_module.get_module_init_code()

    # from .mod_fn import lp
    exec(code, globals())


_init_mod()
print(
    "Run globals().update(vars(libre_pythonista_lib.debug)) to update the current namespace with the contents of this module."
)
