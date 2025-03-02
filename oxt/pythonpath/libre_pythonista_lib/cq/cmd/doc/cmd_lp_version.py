from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_office_doc_t import CmdOfficeDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_doc_custom_prop import CmdDocCustomProp
    from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.qry_lp_version import QryLpVersion
    from oxt.pythonpath.libre_pythonista_lib.const import LP_EXT_VERSION

else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.doc.cmd_office_doc_t import CmdOfficeDocT
    from libre_pythonista_lib.cq.cmd.doc.cmd_doc_custom_prop import CmdDocCustomProp
    from libre_pythonista_lib.cq.query.doc.qry_lp_version import QryLpVersion
    from libre_pythonista_lib.const import LP_EXT_VERSION

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_version.py


class CmdLpVersion(CmdBase, LogMixin, CmdOfficeDocT):
    """Sets the lp version in the document. If it is not current."""

    def __init__(self, doc: OfficeDocumentT) -> None:  # noqa: ANN401
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.doc = doc
        self._config = BasicConfig()
        self._current_state = cast(str | None, NULL_OBJ)

    def _get_current_state(self) -> str | None:  # noqa: ANN401
        qry = QryLpVersion(doc=self.doc)
        return self._execute_qry(qry)

    def _get_cmd_custom(self, value: str | None) -> CmdDocCustomProp:
        # for testing
        return CmdDocCustomProp(doc=self.doc, name=LP_EXT_VERSION, value=value)

    def execute(self) -> None:
        """Executes the command."""
        self.success = False

        try:
            if self._current_state is NULL_OBJ:
                self._current_state = self._get_current_state()
            if self._current_state == self._config.extension_version:
                self.log.debug("Current state exits. Nothing to do.")
                self.success = True
                return
            cmd = self._get_cmd_custom(value=self._config.extension_version)
            self._execute_cmd(cmd)
        except Exception as e:
            self.log.exception("Error calculating all. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if self._current_state is None:
                self.log.debug("Current state is None. Unable to undo.")
                return
            cmd = CmdDocCustomProp(doc=self.doc, name=LP_EXT_VERSION, value=self._current_state)
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
