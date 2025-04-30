from __future__ import annotations
from typing import cast, TYPE_CHECKING, Any

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_office_doc_t import CmdOfficeDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_custom_prop import QryDocCustomProp
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.doc.cmd_office_doc_t import CmdOfficeDocT
    from libre_pythonista_lib.cq.qry.doc.qry_doc_custom_prop import QryDocCustomProp


class CmdDocCustomPropDel(CmdBase, LogMixin, CmdOfficeDocT):
    def __init__(self, doc: OfficeDocumentT, name: str) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.doc = doc
        self.name = name
        self._null = object()
        self._current_state = cast(Any, NULL_OBJ)
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _get_current_state(self) -> Any:  # noqa: ANN401
        qry = QryDocCustomProp(doc=self.doc, name=self.name, default=self._null)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        self.success = False
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()

        try:
            if self.doc.has_custom_property(self.name):  # type: ignore
                self.doc.remove_custom_property(self.name)  # type: ignore
        except Exception as e:
            self.log.exception("Error deleting custom property. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if self._current_state is self._null:
                self.log.debug("Current state is None. Unable to undo.")
                return
            self.doc.set_custom_property(self.name, self._current_state)  # type: ignore
        except Exception as e:
            self.log.exception("Error undoing command. Error: %s", e)
            return
        self.log.debug("Successfully undone command.")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")
