from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile
from ooodev.utils.gen_util import NULL_OBJ
from ooodev.io.sfa.sfa import Sfa

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.qry_doc_props import QryDocProps
else:
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.cq.query.doc.qry_doc_props import QryDocProps


class CmdDocPropsDel(CmdBase, LogMixin, CmdDocT):
    def __init__(self, doc: OfficeDocumentT, file_name: str, root_dir: str = "json", ext: str = "json") -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._sfa = Sfa()
        self._file_name = file_name
        self._ext = ext
        self._doc = doc
        self._root_dir = root_dir
        if ext and not file_name.endswith(ext):
            file_name = f"{file_name}.{ext}"
        self._name = file_name
        self._current_state = cast(Any, NULL_OBJ)

    def _get_current_value(self) -> Any:  # noqa: ANN401
        qry = QryDocProps(doc=self._doc, file_name=self._file_name, ext=self._ext)
        result = self._execute_qry(qry)
        if result is None:
            return None
        return result.read_json(self._name)

    def execute(self) -> None:
        self.success = False
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_value()

        if self._current_state is None:
            self.log.debug("Current state does not exist. Nothing to do.")
            self.success = True
            return

        try:
            self._sfa.delete_file(self._name)
        except Exception as e:
            self.log.exception("Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if self._current_state is None:
                self.log.debug("Current state is None. Unable to undo.")
                return
            djf = DocJsonFile(doc=self._doc, root_dir=self._root_dir)
            djf.write_json(file_name=self._name, data=self._current_state)
        except Exception as e:
            self.log.exception("Error undoing command. Error: %s", e)
            return
        self.log.debug("Successfully undone command.")

    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")
