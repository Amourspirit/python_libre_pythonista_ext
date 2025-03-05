from __future__ import annotations
from abc import ABC, abstractmethod
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import QryT, TResult
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from libre_pythonista_lib.cq.query.qry_handler_t import QryHandlerT
    from libre_pythonista_lib.cq.query.qry_t import QryT, TResult
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdBase(ABC):
    """
    Base class for commands that provides access to command and query handlers.
    """

    def __init__(self) -> None:
        self.__success = False
        self.__kind: CalcCmdKind = CalcCmdKind.SIMPLE
        self.__cmd_handler = None
        self.__qry_handler = None

    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError

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
        if self.__cmd_handler is not None:
            return cast(CmdHandlerT, self.__cmd_handler)

        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
        else:
            from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

        self.__cmd_handler = CmdHandlerFactory.get_cmd_handler()
        return cast(CmdHandlerT, self.__cmd_handler)

    def _get_qry_handler(self) -> QryHandlerT:
        """Get the query handler to execute queries"""
        if self.__qry_handler is not None:
            return cast(QryHandlerT, self.__qry_handler)

        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler_factory import QryHandlerFactory
        else:
            from libre_pythonista_lib.cq.query.qry_handler_factory import QryHandlerFactory

        self.__qry_handler = QryHandlerFactory.get_qry_handler()
        return cast(QryHandlerT, self.__qry_handler)

    def _execute_cmd(self, cmd: CmdT) -> None:
        """Execute a command using the command handler"""
        handler = self._get_cmd_handler()
        handler.handle(cmd)

    def _execute_cmd_undo(self, cmd: CmdT) -> None:
        """Execute a command using the command handler"""
        handler = self._get_cmd_handler()
        handler.handle_undo(cmd)

    def _execute_cmd_redo(self, cmd: CmdT) -> None:
        """Execute a command using the command handler"""
        handler = self._get_cmd_handler()
        handler.handle_redo(cmd)

    def _execute_qry(self, query: QryT[TResult]) -> TResult:
        """Execute a query using the query handler"""
        handler = self._get_qry_handler()
        return handler.handle(query)

    def redo(self) -> None:
        self.execute()

    @abstractmethod
    def undo(self) -> None:
        pass
