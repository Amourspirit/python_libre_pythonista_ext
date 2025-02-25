from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler_t import CmdHandlerT
else:
    from libre_pythonista_lib.cmd.cmd_handler_t import CmdHandlerT


class CmdHandlerFactory:
    """Factory for creating command and query handlers"""

    _cmd_handler: CmdHandlerT | None = None

    @classmethod
    def get_cmd_handler(cls) -> CmdHandlerT:
        """Get the command handler instance"""
        if cls._cmd_handler is None:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
            else:
                from libre_pythonista_lib.cmd.cmd_handler import CmdHandler

            cls._cmd_handler = CmdHandler()
        return cls._cmd_handler

    @classmethod
    def set_cmd_handler(cls, handler: CmdHandlerT) -> None:
        """Set the command handler instance (useful for testing)"""
        cls._cmd_handler = handler

    @classmethod
    def reset(cls) -> None:
        """Reset the factory (useful for testing)"""
        cls._cmd_handler = None
