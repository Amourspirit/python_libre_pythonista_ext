from __future__ import annotations
from typing import cast, TYPE_CHECKING
import time

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from ooodev.utils.data_type.cell_obj import CellObj
    from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySource, PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.pyc.code.py_source import PySource, PySrcProvider
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT


class CmdPySrc(LogMixin, CmdT):
    """Adds new modifier listeners to new sheets"""

    def __init__(self, code: str, uri: str, cell: CellObj, src_provider: PySrcProvider | None = None) -> None:
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False
        self._code = code
        self._py_src = PySource(uri, cell, src_provider)
        self._orig_src = self._py_src.source_code
        self._src_exist = self._py_src.exists()

    def execute(self) -> None:
        self._success = False
        try:
            self._py_src.source_code = self._code
        except Exception:
            self.log.exception("Error initializing setting source code")
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def undo(self) -> None:
        if self._success:
            try:
                if self._src_exist:
                    self._py_src.source_code = self._orig_src
                else:
                    self._py_src.del_source()
                self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error removing Document Event listener")
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def py_src(self) -> PySource:
        return self._py_src
