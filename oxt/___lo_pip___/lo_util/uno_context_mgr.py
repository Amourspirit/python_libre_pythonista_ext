from __future__ import annotations
from typing import Generator
import uno
from contextlib import contextmanager

try:
    import __builtin__  # type: ignore
except ImportError:
    import builtins as __builtin__  # type: ignore


@contextmanager
def uno_suspend_import() -> Generator[None, None, None]:
    try:
        # hook into the __import__ chain
        __builtin__.__dict__["__import__"] = uno._builtin_import  # type: ignore
        yield
    finally:
        __builtin__.__dict__["__import__"] = uno._uno_import  # type: ignore
