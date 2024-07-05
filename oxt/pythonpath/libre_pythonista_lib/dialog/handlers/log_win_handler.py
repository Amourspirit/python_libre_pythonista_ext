from __future__ import annotations
from typing import Any, TYPE_CHECKING, cast, Tuple
import uno
import unohelper

from com.sun.star.awt import XWindowListener
from com.sun.star.awt import XActionListener
from com.sun.star.awt import PosSize  # const
from com.sun.star.awt import Selection

from ooodev.loader import Lo
from ooodev.events.args.event_args import EventArgs
from ooodev.dialog.dl_control import CtlTextEdit
from ooodev.dialog.msgbox import MsgBox, MessageBoxResultsEnum, MessageBoxType, MessageBoxButtonsEnum

from ...log.py_logger import PyLogger
from ...dialog.options.log_opt import LogOpt
from ...log.py_logger import PyLogger
from ...const.event_const import LOG_PY_LOGGER_RESET
from ...event.shared_calc_doc_event import SharedCalcDocEvent

if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlEdit  # service
    from com.sun.star.awt import UnoControlDialog  # service
    from com.sun.star.awt import UnoControlButton  # service

    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .....___lo_pip___.lo_util.resource_resolver import ResourceResolver
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class ButtonListener(unohelper.Base, XActionListener):
    def __init__(self, handler: "LogWinHandler"):
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("ButtonListener.__init__")
        self.handler = handler
        self._log.debug("ButtonListener.__init__ done")

    def disposing(self, ev: Any):
        pass

    def actionPerformed(self, ev: Any):
        # sourcery skip: extract-method
        self._log.debug("ButtonListener.actionPerformed")
        try:
            cmd = str(ev.ActionCommand)
            self._log.debug(f"ButtonListener.actionPerformed cmd: {cmd}")
            if cmd == "LogSettings":

                LogOpt().show()
                return
            if cmd == "ClearLog":
                result = MsgBox.msgbox(
                    title=self.handler.resource_resolver.resolve_string("mbtitle006"),
                    msg=self.handler.resource_resolver.resolve_string("mbmsg006"),
                    boxtype=MessageBoxType.QUERYBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
                )
                if result == MessageBoxResultsEnum.YES:
                    self.handler.clear()
                return

        except Exception as err:
            self._log.error(f"ButtonListener.actionPerformed: {err}", exc_info=True)
            raise err


class LogWinHandler(XWindowListener, unohelper.Base):
    """LogWinHandler Class"""

    def __init__(self, ctx: Any, dialog: UnoControlDialog):
        XWindowListener.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("init")
        try:
            self.ctx = ctx
            self._rr = ResourceResolver(self.ctx)
            self._dialog = dialog
            self.end = 0
            self._init_dialog()
            # reset the logger on Init.
            # this will reset the lp_log global var that can log directly to this window in sheet Python Cells.
            doc = Lo.current_doc
            self._fn_on_log_event = self._on_log_event
            self._fn_on_log_py_inst_reset = self._on_log_py_inst_reset
            self._py_logger = PyLogger(doc=doc)
            self._py_logger.subscribe_log_event(self._fn_on_log_event)
            self._share_event = SharedCalcDocEvent(doc)  # type: ignore
            self._share_event.subscribe_event(LOG_PY_LOGGER_RESET, self._fn_on_log_py_inst_reset)
            PyLogger.reset_instance(doc=doc)

            self._log.debug(f"init Done for Doc with RuntimeID {doc.runtime_uid}")
        except Exception as err:
            self._log.error(f"LogWinHandler.__init__ {err}", exc_info=True)
            raise err

    def _init_dialog(self) -> None:
        btn_listener = ButtonListener(self)
        btn_opt = cast("UnoControlButton", self._dialog.getControl("btnOpt"))
        btn_opt.setActionCommand("LogSettings")
        btn_opt.addActionListener(btn_listener)  # type: ignore
        model = btn_opt.getModel()
        model.Label = self._rr.resolve_string(model.Label)  # type: ignore
        model.HelpText = model.Label  # type: ignore
        self._btn_opt = btn_opt

        btn_clear = cast("UnoControlButton", self._dialog.getControl("btnClear"))
        btn_clear.setActionCommand("ClearLog")
        btn_clear.addActionListener(btn_listener)  # type: ignore
        model = btn_clear.getModel()
        model.Label = self._rr.resolve_string(model.Label)  # type: ignore
        model.HelpText = model.Label  # type: ignore
        self._btn_clear = btn_clear

        self._log_txt = CtlTextEdit(cast("UnoControlEdit", self._dialog.getControl("txtLog")))

    def _on_log_py_inst_reset(self, src: Any, event_args: EventArgs) -> None:
        self._log.debug("_on_log_py_inst_reset")
        try:
            self._py_logger = PyLogger(doc=Lo.current_doc)
            self._py_logger.unsubscribe_log_event(self._fn_on_log_event)
            self._py_logger.subscribe_log_event(self._fn_on_log_event)
        except Exception:
            self._log.exception("_on_log_py_inst_reset")

    def _on_log_event(self, src: Any, event: EventArgs) -> None:
        if self._log.is_debug:
            self._log.debug("_on_log_event, Writing Line")
        self._write_line(event.event_data.log_msg)

    def _write_line(self, text: str) -> None:
        self._log_txt.write_line(text)

    def _write(self, data: str, sel: Tuple[int, int] | None = None):
        """Append data to edit control text"""
        if not sel:
            sel = (self.end, self.end)
        # sel = (0, 0)
        self._log_txt.view.insertText(Selection(*sel), data)

    def clear(self) -> None:
        """Clears the Log Text."""
        self._log_txt.text = ""

    def resize(self, width: int, height: int) -> None:
        """Triggers resize of controls."""
        self._log_txt.view.setPosSize(0, 0, width - 5, height - 40, PosSize.SIZE)

    @property
    def dialog(self) -> UnoControlDialog:
        return self._dialog

    @property
    def resource_resolver(self) -> ResourceResolver:
        return self._rr
