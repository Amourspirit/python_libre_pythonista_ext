from __future__ import annotations
from typing import Any, cast, Tuple, TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile
from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_json_file import QryDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from libre_pythonista_lib.cq.qry.doc.qry_doc_json_file import QryDocJsonFile
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdDocJsonFileDel(CmdBase, LogMixin, CmdCacheT):
    def __init__(self, doc: OfficeDocumentT, file_name: str, root_dir: str = "json", ext: str = "json") -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.SIMPLE_CACHE
        self.file_name = file_name
        self.ext = ext
        self.doc = doc
        self.root_dir = root_dir
        if ext and not file_name.endswith(ext):
            file_name = f"{file_name}.{ext}"
        self.name = file_name
        self._current_state = cast(DocJsonFile | None, NULL_OBJ)
        self._current_value = cast(Any, NULL_OBJ)

    def _get_current_state(self) -> DocJsonFile | None:
        qry = QryDocJsonFile(doc=self.doc, file_name=self.file_name, ext=self.ext)
        return self._execute_qry(qry)

    def _get_current_value(self, js: DocJsonFile) -> Any:  # noqa: ANN401
        return js.read_json(self.name)

    @override
    def execute(self) -> None:
        self.success = False
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()

        if self._current_state is None:
            self.log.debug("Current state does not exist. Nothing to do.")
            self.success = True
            return

        if self._current_value is NULL_OBJ:
            self._current_value = self._get_current_value(self._current_state)

        try:
            self._current_state.delete_file(self.name)
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
            djf = DocJsonFile(doc=self.doc, root_dir=self.root_dir)
            djf.write_json(file_name=self.name, data=self._current_value)
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

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (f"DocJsonFile_{self.name}",)
