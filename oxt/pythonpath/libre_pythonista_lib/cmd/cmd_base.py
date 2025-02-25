from __future__ import annotations
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT, TResult
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cmd.cmd_handler_t import CmdHandlerT
    from libre_pythonista_lib.query.qry_handler_t import QryHandlerT
    from libre_pythonista_lib.query.qry_t import QryT, TResult
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdBase:
    """
    Base class for commands that provides access to command and query handlers.
    """

    def __init__(self) -> None:
        self.__success = False
        self.__kind: CalcCmdKind = CalcCmdKind.SIMPLE

    @property
    def success(self) -> bool:
        return self.__success

    @success.setter
    def success(self, value: bool) -> None:
        self.__success = value

    @property
    def kind(self) -> CalcCmdKind:
        return self.__kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self.__kind = value

    def _get_cmd_handler(self) -> CmdHandlerT:
        """Get the command handler to execute other commands"""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler_factory import CmdHandlerFactory
        else:
            from libre_pythonista_lib.cmd.cmd_handler_factory import CmdHandlerFactory

        return CmdHandlerFactory.get_cmd_handler()

    def _get_qry_handler(self) -> QryHandlerT:
        """Get the query handler to execute queries"""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.query.qry_handler_factory import QryHandlerFactory
        else:
            from libre_pythonista_lib.query.qry_handler_factory import QryHandlerFactory

        return QryHandlerFactory.get_qry_handler()

    def _execute_cmd(self, cmd: CmdT) -> None:
        """Execute a command using the command handler"""
        handler = self._get_cmd_handler()
        handler.handle(cmd)

    def _execute_qry(self, query: QryT[TResult]) -> TResult:
        """Execute a query using the query handler"""
        handler = self._get_qry_handler()
        return handler.handle(query)
