from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.loader import Lo

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.sheet.listen.code_sheet_modify_listener import CodeSheetModifyListener
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdSheetsModified(LogMixin, CmdT):
    """Adds Sheet Modified listeners to all sheets that don't have one"""

    def __init__(self) -> None:
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False
        self._unique_ids = set()

    def execute(self) -> None:
        self._success = False
        try:
            self._unique_ids.clear()
            for sheet in self._doc.sheets:
                unique_id = sheet.unique_id
                if CodeSheetModifyListener.has_listener(unique_id):
                    listener = CodeSheetModifyListener.get_listener(unique_id)  # singleton
                    listener.set_trigger_state(True)
                    sheet.component.removeModifyListener(listener)
                    sheet.component.addModifyListener(listener)
                else:
                    listener = CodeSheetModifyListener(unique_id)  # singleton
                    listener.set_trigger_state(True)
                    sheet.component.addModifyListener(listener)
                    self._unique_ids.add(unique_id)
            self.log.debug("Successfully executed command.")
        except Exception:
            self.log.exception("Error initializing sheet listeners")
            return
        self._success = True

    def undo(self) -> None:
        if self._success:
            try:
                for sheet in self._doc.sheets:
                    unique_id = sheet.unique_id
                    if unique_id in self._unique_ids and CodeSheetModifyListener.has_listener(unique_id):
                        listener = CodeSheetModifyListener(unique_id)
                        # removing this listener from the document does not seem to work.
                        # by setting the trigger to False, we can prevent the listener from firing.
                        listener.set_trigger_state(False)
                        sheet.component.removeModifyListener(listener)
                self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error removing sheet activation listener")
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def kind(self) -> CalcCmdKind:
        return CalcCmdKind.SIMPLE
