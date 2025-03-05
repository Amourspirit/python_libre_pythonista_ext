from __future__ import annotations
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_props import QryLpDocProps
    from pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
    from libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_props import QryLpDocProps
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_doc_prop.py


class CmdLpDocProp(CmdBase, LogMixin, CmdDocT):
    """Set the custom property of the document"""

    def __init__(self, doc: CalcDoc, name: str, value: Any) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self._name = name
        self._value = value
        self._ensured_file = False

    def _ensure_json_file(self) -> bool:
        qry = QryLpDocJsonFile(self._doc)
        result = self._execute_qry(qry)
        if result is None:
            cmd = CmdLpDocJsonFile(self._doc)
            self._execute_cmd(cmd)
        return True

    @override
    def execute(self) -> None:
        if self._ensured_file is False:
            self._ensured_file = self._ensure_json_file()

        self.success = False
        try:
            qry = QryLpDocProps(self._doc)
            results = self._execute_qry(qry)
            if results is None:
                results = {}
            results[self._name] = self._value
            cmd = CmdLpDocProps(self._doc, results)
            self._execute_cmd(cmd)
        except Exception:
            self.log.exception("Error setting document property.")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        self.log.debug("Undo not needed for this command.")
