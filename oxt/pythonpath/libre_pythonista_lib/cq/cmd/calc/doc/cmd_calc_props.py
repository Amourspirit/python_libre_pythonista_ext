from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_calc_props import QryCalcProps
    from oxt.pythonpath.libre_pythonista_lib.doc_props.calc_props2 import CalcProps2
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS, DOC_LP_DOC_PROP_DATA
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_props import CmdLpDocProps
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from libre_pythonista_lib.cq.query.calc.doc.qry_calc_props import QryCalcProps
    from libre_pythonista_lib.doc_props.calc_props2 import CalcProps2
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin

# tested in tests/test_cmd_qry/test_doc/test_cmd_calc_props.py


class CmdCalcProps(CmdBase, LogMixin, CmdCacheT):
    """
    Set calc properties in the document.

    Ensures that the calc properties exist.
    """

    def __init__(self, doc: CalcDoc, props: CalcProps2) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.SIMPLE_CACHE
        self._doc = doc
        self._props = props
        self._current_props = cast(CalcProps2, NULL_OBJ)

    def _get_current_props(self) -> CalcProps2:
        qry = QryCalcProps(self._doc)
        return self._execute_qry(qry)

    def execute(self) -> None:
        self.success = False
        try:
            if self._current_props is NULL_OBJ:
                self._current_props = self._get_current_props()

            cmd = CmdLpDocProps(doc=self._doc, props=self._props.to_dict())
            self._execute_cmd(cmd)
        except Exception as e:
            self.log.exception("Error setting calc properties. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    def _undo(self) -> None:
        try:
            cmd = CmdLpDocProps(doc=self._doc, props=self._current_props.to_dict())
            self._execute_cmd(cmd)
        except Exception as e:
            self.log.exception("Error undoing command. Error: %s", e)
            return
        self.log.debug("Successfully undone command.")

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        """Gets the cache keys."""
        return (
            DOC_CALC_PROPS,
            DOC_LP_DOC_PROP_DATA,
        )
