from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile
from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_json_file import QryDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from libre_pythonista_lib.cq.qry.doc.qry_doc_json_file import QryDocJsonFile
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result


# tested in tests/test_cmd/test_cmd_lp_doc_json_file.py


class CmdDocJsonFile(CmdBase, LogMixin, CmdCacheT):
    """
    Ensures that the document json file exists.
    This class is used to ensure that the document json file exists.

    This class uses a cache key to ensure that the document json file is only created once.
    """

    def __init__(self, doc: OfficeDocumentT, file_name: str, root_dir: str = "json", ext: str = "json") -> None:
        """Constructor

        Args:
            doc (OfficeDocumentT): Document to create the json file for.
            file_name (str): Name of the json file.
            root_dir (str, optional): Root directory of the json file. Defaults to "json".
            ext (str, optional): Extension of the json file. Defaults to "json".
        """
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

    def _get_current_value(self) -> DocJsonFile | None:
        qry = QryDocJsonFile(doc=self.doc, file_name=self.file_name, root_dir=self.root_dir, ext=self.ext)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    @override
    def execute(self) -> None:
        """Executes the command."""
        self.success = False
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_value()
        if self._current_state is not None:
            self.log.debug("Current state exits. Nothing to do.")
            self.success = True
            return

        try:
            djf = DocJsonFile(self.doc, "json")
            djf.write_json(self.name, {})
        except Exception as e:
            self.log.exception("Error calculating all. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_doc_json_file_del import CmdDocJsonFileDel
            else:
                from libre_pythonista_lib.cq.cmd.doc.cmd_doc_json_file_del import CmdDocJsonFileDel

            cmd = CmdDocJsonFileDel(doc=self.doc, file_name=self.name, root_dir=self.root_dir, ext=self.ext)
            self._execute_cmd(cmd)
        except Exception as e:
            self.log.exception("Error undoing command. Error: %s", e)
            return
        self.log.debug("Successfully undone command.")

    @override
    def undo(self) -> None:
        """Undoes the command."""
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (f"DocJsonFile_{self.name}",)
