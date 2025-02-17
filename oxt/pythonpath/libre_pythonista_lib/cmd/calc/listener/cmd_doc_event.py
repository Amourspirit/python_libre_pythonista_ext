from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.doc.listen.document_event_listener import DocumentEventListener
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.doc.listen.document_event_listener import DocumentEventListener
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdDocEvent(LogMixin, CmdT):
    """Adds new modifier listeners to new sheets"""

    def __init__(self) -> None:
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._listener = None
        self._success = False

    def execute(self) -> None:
        self._success = False
        try:
            self._listener = DocumentEventListener()  # singleton
            self._listener.set_trigger_state(True)
            self._doc.component.addDocumentEventListener(self._listener)
        except Exception:
            self.log.exception("Error initializing Document Event listener")
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def undo(self) -> None:
        if self._success and self._listener is not None:
            try:
                self._listener.set_trigger_state(False)
                self._doc.component.removeDocumentEventListener(self._listener)
                self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error removing Document Event listener")
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def kind(self) -> CalcCmdKind:
        return CalcCmdKind.SIMPLE
