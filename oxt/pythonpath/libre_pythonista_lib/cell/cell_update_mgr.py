"""Manages updating cells that may need updating on startup"""

from __future__ import annotations
from typing import TYPE_CHECKING
import uno
from ooodev.calc import CalcDoc
from ..code.py_source_mgr import PyInstance
from .ctl.ctl_mgr import CtlMgr
from ..doc_props.calc_props import CalcProps

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config


class CellUpdateMgr:
    """
    Manages updating cell controls that have moved from user to shared or vice versa.
    """

    def __init__(self, doc: CalcDoc):
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug("Init")
        self._doc = CalcDoc
        self._py_inst = PyInstance(doc)
        self._ctl_mgr = CtlMgr()
        self._calc_props = CalcProps(doc)
        self._cfg = Config()

    def _is_location_valid(self) -> bool:
        if self._cfg.is_shared_installed:
            current_location = "share"
        else:
            current_location = "user"
        return self._calc_props.doc_ext_location == current_location

    def update_cells(self):
        """
        Update cells that may need updating on startup.

        If the extension location is the same then no action is taken.
        """
        with self._log.indent(True):
            self._log.debug("Update Cells Entered")
            if self._is_location_valid():
                self._log.debug("Current Extension location is valid. Nothing to update.")
                return

            try:
                cells = self._py_inst.get_calc_cells()
                if not cells:
                    self._log.debug("No cells to update.")
                    return
                for cell in cells:
                    self._ctl_mgr.update_ctl_script(cell)
                self._log.debug(f"Update Script Location for {len(cells)} Cells.")
            except Exception:
                self._log.exception("Error updating cells")
            self._log.debug("Update Cells Exit")
