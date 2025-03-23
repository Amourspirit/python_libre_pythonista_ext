from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile
from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
    from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.utils.result import Result

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_doc_prop.py


class CmdLpDocProps(CmdBase, LogMixin, CmdCacheT):
    """
    Set properties in the document.

    Ensures that the document json file exists.
    """

    def __init__(self, doc: CalcDoc, props: dict) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.SIMPLE_CACHE
        self._doc = doc
        self._props = props
        self._file_name = ""
        self._json_file = cast(DocJsonFile | None, NULL_OBJ)
        self._ensured = False
        self._current_state = cast(dict | None, NULL_OBJ)

    def _ensure_json_file(self) -> bool:
        qry = QryLpDocJsonFile(self._doc)
        result = self._execute_qry(qry)
        if Result.is_failure(result):
            cmd = CmdLpDocJsonFile(self._doc)
            self._execute_cmd(cmd)
        return True

    def _get_json_file(self) -> DocJsonFile | None:
        qry = QryLpDocJsonFile(self._doc)
        self._file_name = qry.file_name
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    @override
    def execute(self) -> None:
        if self._ensured is False:
            self._ensured = self._ensure_json_file()

        json_file = self._get_json_file()

        if json_file is None:
            self.log.debug("JSON file does not exist. Nothing to do.")
            self.success = True
            return

        if self._current_state is NULL_OBJ:
            self._current_state = json_file.read_json(self._file_name)

        self.success = False
        try:
            json_file.write_json(file_name=self._file_name, data=self._props)
        except Exception as e:
            self.log.exception("Error setting document properties. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    def _undo(self) -> None:
        if self._current_state is NULL_OBJ:
            self.log.debug("Current state is None. Unable to undo.")
            return
        if self._json_file is None:
            self.log.debug("JSON file does not exist. Unable to undo.")
            return
        try:
            data = {} if self._current_state is None else self._current_state
            self._json_file.write_json(file_name=self._file_name, data=data)
        except Exception as e:
            self.log.exception("Error undoing command. Error: %s", e)
            return
        self.log.debug("Successfully undone command.")

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        """Gets the cache keys."""
        return (DOC_LP_DOC_PROP_DATA,)
