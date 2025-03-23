from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_pyc_formula import (
        QryCellIsPycFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )
else:
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_pyc_formula import QryCellIsPycFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners

_KEY = "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_event_mgr.CellEventMgr"


class CellEventMgr(LogMixin):
    def __new__(cls, src_mgr: PySourceManager) -> CellEventMgr:
        gbl_cache = DocGlobals.get_current(src_mgr.doc.runtime_uid)
        src_mgr_id = id(src_mgr)
        key = f"{_KEY}_{src_mgr_id}"
        if key in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[key]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[key] = inst
        return inst

    def __init__(self, src_mgr: PySourceManager) -> None:
        """
        Constructor

        Args:
            src_mgr (PySourceManager): The source manager to manage events for.
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self._se = SharedEvent(src_mgr.doc)
        self._src_mgr = src_mgr
        self._listeners = CodeCellListeners(src_mgr.doc)
        self._init_events()
        self._is_init = True

    def _init_events(self) -> None:
        self._fn_on_cell_deleted = self.on_cell_deleted
        self._fn_on_cell_moved = self.on_cell_moved
        self._fn_on_cell_pyc_formula_removed = self.on_cell_pyc_formula_removed
        self._fn_on_cell_modified = self.on_cell_modified

    def _qry_is_pyc_formula(self, calc_cell: CalcCell) -> bool:
        qry = QryCellIsPycFormula(cell=calc_cell)
        return self._src_mgr.qry_handler.handle(qry)

    def _qry_code_name(self, calc_cell: CalcCell) -> str:
        qry = QryCodeName(cell=calc_cell)
        return self._src_mgr.qry_handler.handle(qry)

    def _remove_cell(self, calc_cell: CalcCell) -> None:
        """Removes cell from Py Source Manager, listener, and Cell Control."""
        # - Remove from Listeners
        # - Remove Source code
        # - Remove from PySourceManager
        # - Remove Cell Control
        facade = CellItemFacade(calc_cell)
        facade.remove_control()
        self._listeners.remove_listener(calc_cell)
        self._src_mgr.remove_source(calc_cell.cell_obj)

    def on_cell_deleted(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        """
        Event handler for when a cell is deleted.

        ``CalcCell.extra_data`` of event_data will the same key value pairs of the event_data keys.

        ``EventArgs.event_data`` and ``EventArgs.event_data.calc_cell.extra_data`` will have the following

        - absolute_name: str
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - calc_cell: CalcCell
        - deleted: True
        - cell_info: CellInfo


        """
        dd = cast(DotDict, event.event_data)
        dd.absolute_name = dd.get("absolute_name", "UNKNOWN")
        self.log.debug("on_cell_deleted() Entering.")
        self._remove_cell(calc_cell=dd.calc_cell)
        self.log.debug("Cell deleted: %s", dd.absolute_name)

    def on_cell_moved(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        """
        Event handler for when a cell is moved.

        ``EventArgs.event_data`` is a DotDict with the following keys:
        - absolute_name: current cell absolute name.
        - old_name: old cell absolute name.
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - cell_info: CellInfo
        - calc_cell: CalcCell
        - deleted: False

        """
        dd = cast(DotDict, event.event_data)
        dd.absolute_name = dd.get("absolute_name", "UNKNOWN")
        calc_cell = cast(CalcCell, dd.calc_cell)
        cmd = CmdAddr(cell=calc_cell)
        self._src_mgr.cmd_handler.handle(cmd)
        if not cmd.success:
            self.log.error("Failed to update cell address property for %s", dd.absolute_name)
            return
        self.log.debug("Cell moved: %s", dd.absolute_name)

    def on_cell_pyc_formula_removed(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        """
        Event handler for when a cell has pyc formula removed.

        ``EventArgs.event_data`` and ``EventArgs.event_data.calc_cell.extra_data`` will have the following:

        - absolute_name: current cell absolute name.
        - old_name: old cell absolute name.
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - calc_cell: CalcCell
        - deleted: False

        """
        dd = cast(DotDict, event.event_data)
        dd.absolute_name = dd.get("absolute_name", "UNKNOWN")
        try:
            self.log.debug("on_cell_pyc_formula_removed() Entering.")
            self._remove_cell(calc_cell=dd.calc_cell)
            self.log.debug("on_cell_pyc_formula_removed() Leaving: %s", dd.absolute_name)
        except Exception:
            self.log.exception("Error removing pyc formula from cell: %s", dd.absolute_name)

    def on_cell_modified(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        """
        Event handler for when a cell is modified.

        ``CalcCell.extra_data`` of event_data will the same key value pairs of the event_data keys.

        ``EventArgs.event_data`` and ``EventArgs.event_data.calc_cell.extra_data`` will have the following:

        - absolute_name: str
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - calc_cell: CalcCell
        - deleted: False
        - cell_info: CellInfo

        """
        dd = cast(DotDict, event.event_data)
        dd.absolute_name = dd.get("absolute_name", "UNKNOWN")
        try:
            calc_cell = cast(CalcCell, dd.calc_cell)
            is_pyc_formula = self._qry_is_pyc_formula(calc_cell)

            if not is_pyc_formula:
                self.log.debug(
                    "Formula has been modified or removed. Not a LibrePythonista cell: %s", dd.absolute_name
                )
                # address = cell.getCellAddress()
                self._remove_cell(calc_cell=dd.calc_cell)
            if self.log.is_debug:
                is_first_cell = getattr(dd, "is_first_cell", False)
                is_last_cell = getattr(dd, "is_last_cell", False)
                self.log.debug("Is First Cell: %s", is_first_cell)
                self.log.debug("Is Last Cell: %s", is_last_cell)
        except Exception:
            self.log.exception("Error modifying cell: %s", dd.absolute_name)

        self.log.debug("Cell modified: %s", dd.absolute_name)
