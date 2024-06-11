from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.loader import Lo
from ooodev.calc import CalcDoc
from ..dialog.py.dialog_python import DialogPython
from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.sheet import SheetCellCursor
    from ooodev.utils.data_type.cell_obj import CellObj
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ..code.py_source_mgr import PyInstance
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from libre_pythonista_lib.code.py_source_mgr import PyInstance


class DispatchEditPY(unohelper.Base, XDispatch):
    def __init__(self, sheet: str, cell: str):
        self._sheet = sheet
        self._cell = cell
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug(f"init: sheet={sheet}, cell={cell}")

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        pass

    def dispatch(self, url: URL, args: Tuple[PropertyValue, ...]) -> None:
        """
        Dispatches (executes) a URL

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        self._logger.debug(f"dispatch(): url={url}")
        doc = CalcDoc.from_current_doc()
        sheet = doc.sheets[self._sheet]
        cell = sheet[self._cell]
        cc = CellCache(doc)  # singleton
        cell_obj = cell.cell_obj
        sheet_idx = sheet.sheet_index
        if not cc.has_cell(cell=cell_obj, sheet_idx=sheet_idx):
            self._logger.error(f"Cell {self._cell} is not in the cache.")
            return
        with cc.set_context(cell=cell_obj, sheet_idx=sheet_idx):
            result = self._edit_code(doc=doc, cell_obj=cell_obj)
            if result:
                if doc.component.isAutomaticCalculationEnabled():
                    cm = CellMgr(doc)  # singleton. Tracks all Code cells
                    # https://ask.libreoffice.org/t/mark-a-calc-sheet-cell-as-dirty/106659
                    with cm.listener_context(cell.component):
                        # suspend the listeners for this cell
                        formula = cell.component.getFormula()
                        if not formula:
                            self._logger.error(f"Cell {self._cell} has no formula.")
                            return
                        # s = s.lstrip("=")  # just in case there are multiple equal signs
                        is_formula_array = False
                        if formula.startswith("{"):
                            is_formula_array = True
                            formula = formula.lstrip("{")
                            formula = formula.rstrip("}")
                        if is_formula_array:
                            try:
                                self._logger.debug("Resetting array formula")
                                cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
                                # this next line also works.
                                # cursor = cast("SheetCellCursor", cell.component.getSpreadsheet().createCursorByRange(cell.component))  # type: ignore
                                cursor.collapseToCurrentArray()
                                cursor.setArrayFormula(formula)
                            except Exception:
                                self._logger.error("Error setting array formula", exc_info=True)
                        else:
                            self._logger.debug("Resetting formula")
                            cell.component.setFormula(formula)
                        doc.component.calculate()

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        pass

    def _edit_code(self, doc: CalcDoc, cell_obj: CellObj) -> bool:
        ctx = Lo.get_context()
        dlg = DialogPython(ctx)
        py_inst = PyInstance(doc)  # singleton
        py_src = py_inst[cell_obj]
        code = py_src.source_code
        py_src = None
        self._logger.debug("Displaying dialog")
        dlg.text = code
        result = False
        if dlg.show():
            self._logger.debug("Dialog returned with OK")
            txt = dlg.text.strip()
            if txt != code:
                try:
                    self._logger.debug("Code has changed, updating ...")
                    py_inst.update_source(code=txt, cell=cell_obj)
                    self._logger.debug(f"Cell Code updated for {cell_obj}")
                    py_inst.update_all()
                    self._logger.debug("Code updated")
                    result = True
                except Exception as e:
                    self._logger.error("Error updating code", exc_info=True)
            else:
                self._logger.debug("Code has not changed")
        else:
            self._logger.debug("Dialog returned with Cancel")
        return result
