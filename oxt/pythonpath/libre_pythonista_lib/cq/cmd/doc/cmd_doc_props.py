from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile
from ooodev.utils.gen_util import NULL_OBJ

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


class CmdDocProps(CmdBase, LogMixin, CmdDocT):
    def __init__(self, doc: OfficeDocumentT, file_name: str, root_dir: str = "json", ext: str = "json") -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._file_name = file_name
        self._ext = ext
        self._doc = doc
        self._root_dir = root_dir
        if ext and not file_name.endswith(ext):
            file_name = f"{file_name}.{ext}"
        self._name = file_name
        self._current_state = cast(DocJsonFile | None, NULL_OBJ)

    def _get_current_value(self) -> DocJsonFile | None:
        qry = QryDocProps(doc=self._doc, file_name=self._file_name, root_dir=self._root_dir, ext=self._ext)
        return self._execute_qry(qry)

    def execute(self) -> None:
        self.success = False
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_value()
        if self._current_state is not None:
            self.log.debug("Current state exits. Nothing to do.")
            self.success = True
            return

        try:
            djf = DocJsonFile(self._doc, "json")
            djf.write_json(self._name, {})
        except Exception as e:
            self.log.exception("Error calculating all. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_doc_props_del import CmdDocPropsDel
            else:
                from libre_pythonista_lib.cq.cmd.doc.cmd_doc_props_del import CmdDocPropsDel

            cmd = CmdDocPropsDel(doc=self._doc, file_name=self._name, root_dir=self._root_dir, ext=self._ext)
            self._execute_cmd(cmd)
        except Exception as e:
            self.log.exception("Error undoing command. Error: %s", e)
            return
        self.log.debug("Successfully undone command.")

    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")
