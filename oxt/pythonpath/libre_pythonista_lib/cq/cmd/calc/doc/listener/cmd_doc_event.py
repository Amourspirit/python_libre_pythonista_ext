from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.listen.document_event_listener import DocumentEventListener
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
else:
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.doc.listen.document_event_listener import DocumentEventListener
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT


class CmdDocEvent(CmdBase, LogMixin, CmdDocT):
    """Adds new modifier listeners to new sheets"""

    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self._listener = None

    def execute(self) -> None:
        self.success = False
        try:
            self._listener = DocumentEventListener()  # singleton
            self._listener.set_trigger_state(True)
            self._doc.component.addDocumentEventListener(self._listener)
        except Exception:
            self.log.exception("Error initializing Document Event listener")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def undo(self) -> None:
        if self.success and self._listener is not None:
            try:
                self._listener.set_trigger_state(False)
                self._doc.component.removeDocumentEventListener(self._listener)
                self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error removing Document Event listener")
        else:
            self.log.debug("Undo not needed.")
