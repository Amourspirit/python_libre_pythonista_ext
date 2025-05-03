from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Union

from ooodev.utils.gen_util import NULL_OBJ
from ooodev.conn.connect_ctx import ConnectCtx
from ooodev.loader.inst.options import Options
from ooodev.loader import Lo
from ooodev.loader.inst.lo_inst import LoInst

if TYPE_CHECKING:
    from com.sun.star.uno import XComponentContext
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_CTX_LOADED
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_current_ctx_loaded import QryCurrentCtxLoaded
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.const.cache_const import DOC_CTX_LOADED
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.qry.doc.qry_current_ctx_loaded import QryCurrentCtxLoaded
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result

    XComponentContext = Any


# tested in tests/test_cmd/test_cmd_lp_doc_json_file.py


class CmdCurrentCtxLoad(CmdBase, LogMixin, CmdT):
    def __init__(self, ctx: object, uid: Union[str, None] = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.SIMPLE
        self._ctx = ctx
        self._uid = uid
        self._state_changed = False
        self._current_state = cast(Union[XComponentContext, None], NULL_OBJ)
        self._current_lo_inst = cast(Union[LoInst, None], NULL_OBJ)
        self._current_options = cast(Union[Options, None], NULL_OBJ)
        self.log.debug("init done")

    def _qry_globals(self) -> Union[Result[DocGlobals, None], Result[None, Exception]]:
        """
        Get the document globals using QryDocGlobals.

        Returns:
            Result: Success with DocGlobals or Failure with None/Exception
        """
        qry = QryDocGlobals(uid=self._uid)
        return self._execute_qry(qry)

    def _qry_current_ctx_loaded(self) -> bool:
        qry = QryCurrentCtxLoaded(uid=self._uid)
        return self._execute_qry(qry)

    def _load_from_ctx(self, ctx: object) -> None:
        """Loads the current context from the context."""
        if self._current_options is None:
            opt = Options(force_reload=True)
        else:
            opt = Options(
                verbose=self._current_options.verbose,
                dynamic=self._current_options.dynamic,
                log_level=self._current_options.log_level,
                lo_cache_size=self._current_options.lo_cache_size,
                force_reload=True,
            )
        connect_ctx = ConnectCtx(ctx=ctx)  # type: ignore
        _ = Lo.load_office(connector=connect_ctx, opt=opt)

    def _get_current_options(self) -> Union[Options, None]:
        """Gets the current options."""
        try:
            if self._current_lo_inst is None:
                return None
            return self._current_lo_inst.options
        except Exception as e:
            self.log.exception("Error getting current options. Error: %s", e)
            return None

    @override
    def execute(self) -> None:
        """Executes the command."""
        self.success = False
        self._state_changed = False

        doc_globals = self._qry_globals()
        if Result.is_failure(doc_globals):
            self.log.error("DocGlobals is None. Unable to execute command.")
            return

        if self._ctx is None:
            self.log.error("Context is None. Unable to execute command.")
            return

        if self._qry_current_ctx_loaded():
            self.log.debug("Current context is already loaded. Nothing to do.")
            self.success = True
            return

        if self._current_lo_inst is NULL_OBJ:
            try:
                self._current_lo_inst = Lo.current_lo
            except Exception:
                self._current_lo_inst = None

        if self._current_state is NULL_OBJ:
            try:
                if self._current_lo_inst is None:
                    self._current_state = None
                else:
                    self._current_state = self._current_lo_inst.get_context()
            except Exception:
                self._current_state = None

        if self._current_options is NULL_OBJ:
            self._current_options = self._get_current_options()

        try:
            self._load_from_ctx(self._ctx)
            doc_globals.data.mem_cache[DOC_CTX_LOADED] = "1"
        except Exception as e:
            self.log.exception("Error calculating all. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            if not self._state_changed:
                self.log.debug("State has not changed. Undo not needed.")
                return
            if self._current_state is None:
                self.log.debug("Current state is None. Unable to undo.")
                return
            doc_globals = self._qry_globals()
            if Result.is_failure(doc_globals):
                self.log.error("DocGlobals is None. Unable to execute command.")
                return
            self._load_from_ctx(self._current_state)
            doc_globals.data.mem_cache[DOC_CTX_LOADED] = "0"
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
