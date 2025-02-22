from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdCalculateAll(LogMixin, CmdDocT):
    """Calculate all cells in the document"""

    def __init__(self, doc: CalcDoc) -> None:
        LogMixin.__init__(self)
        self._success = False
        self._doc = doc
        self._kind = CalcCmdKind.SIMPLE

    def execute(self) -> None:
        self._success = False
        try:
            self._doc.component.calculateAll()
        except Exception as e:
            self.log.exception("Error calculating all. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def undo(self) -> None:
        self.log.debug("Undo not needed for this command.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.SIMPLE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
