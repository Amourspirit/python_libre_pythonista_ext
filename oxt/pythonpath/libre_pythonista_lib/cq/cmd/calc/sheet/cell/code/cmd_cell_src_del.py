from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELL_SRC_CODE_EXIST
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_py_source import QryCellPySource
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code_exist import (
        QryCellSrcCodeExist,
    )

else:
    from libre_pythonista_lib.const.cache_const import CELL_SRC_CODE_EXIST
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_py_source import QryCellPySource
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.code.qry_cell_src_code_exist import QryCellSrcCodeExist
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.null import NULL
    from libre_pythonista_lib.utils.result import Result


class CmdCellSrcDel(CmdBase, LogMixin, CmdCellCacheT):
    """
    Command to delete source code from a cell.

    This class implements the Command pattern to handle deletion of Python source code
    associated with a cell, with support for undo operations.

    Args:
        cell (CalcCell): The cell containing the source code to delete

    Properties:
        cell (CalcCell): The target cell
        cache_keys (Tuple[str, ...]): Keys used for caching
        uri (str): URI identifier for the cell
    """

    def __init__(self, cell: CalcCell) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL_CACHE
        self._cell = cell
        self._uri = None
        self._cell_deleted = None
        self._current_py_src = cast(PySource, None)
        self._current_exist = None
        self._current_src = ""
        self._cell_code_name = NULL

    def _qry_is_deleted(self) -> bool:
        """Check if the cell has been deleted."""
        qry = QryCellIsDeleted(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_cell_uri(self) -> str:
        """Get the URI identifier for the cell."""
        qry = QryCellUri(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_py_src(self) -> PySource:
        """Get the Python source associated with the cell."""
        qry = QryCellPySource(uri=self.uri, cell=self.cell)
        return self._execute_qry(qry)

    def _get_src_code_exist(self) -> bool:
        """Check if source code exists for the cell."""
        qry = QryCellSrcCodeExist(uri=self.uri, cell=self.cell)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Execute the delete command.

        Deletes the source code if it exists. Sets success flag to True if operation succeeds.
        """
        self.success = False

        try:
            if self._cell_code_name is NULL:
                if "code_name" in self.cell.extra_data:
                    self._cell_code_name = self.cell.extra_data["code_name"]
                else:
                    self._cell_code_name = None

            if self._cell_deleted is None:
                self._cell_deleted = self._qry_is_deleted()

            if self._current_py_src is None:
                self._current_py_src = self._qry_py_src()

            if self._current_exist is None:
                self._current_exist = self._current_py_src.exists()
                self._current_src = self._current_py_src.source_code

            if not self._current_py_src.exists():
                self.log.debug("Source code does not exist. Nothing to delete.")
                self.success = True
                return
            self._current_py_src.del_source()

            # do not remove code_name from extra data here it may be used in
            # other places such as cq.qry.calc.sheet.cell.prop.qry_code_name.QryCodeName
            # if "code_name" in self.cell.extra_data:
            #     del self.cell.extra_data["code_name"]
        except Exception:
            self.log.exception("Error deleting cell Code")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to restore the previously deleted source code.

        Restores the source code if the cell still exists and had source code before deletion.
        """
        try:
            if self._cell_deleted is None:
                self._cell_deleted = self._qry_is_deleted()
            if self._cell_deleted:
                self.log.debug("Cell is deleted. Nothing to undo.")
                return
            if self._current_exist:
                py_code = PySource(uri=self.uri, cell=self.cell.cell_obj)
                py_code.source_code = self._current_src

            # if self._cell_code_name:
            #     self.cell.extra_data["code_name"] = self._cell_code_name

            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code")

    @override
    def undo(self) -> None:
        """
        Undo the delete operation if it was successful.

        Only attempts to undo if the original delete operation succeeded.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (CELL_SRC_CODE_EXIST,)

    @property
    def uri(self) -> str:
        if self._uri is None:
            self._uri = self._qry_cell_uri()
        return self._uri
