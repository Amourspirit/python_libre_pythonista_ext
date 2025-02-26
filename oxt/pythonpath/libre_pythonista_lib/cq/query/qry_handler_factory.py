from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler_t import QryHandlerT
else:
    from libre_pythonista_lib.cq.query.qry_handler_t import QryHandlerT


class QryHandlerFactory:
    """Factory for creating query handlers"""

    _qry_handler: QryHandlerT | None = None

    @classmethod
    def get_qry_handler(cls) -> QryHandlerT:
        """Get the query handler instance"""
        if cls._qry_handler is None:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
            else:
                from libre_pythonista_lib.cq.query.qry_handler import QryHandler

            cls._qry_handler = QryHandler()
        return cls._qry_handler

    @classmethod
    def set_qry_handler(cls, handler: QryHandlerT) -> None:
        """Set the query handler instance (useful for testing)"""
        cls._qry_handler = handler

    @classmethod
    def reset(cls) -> None:
        """Reset the factory (useful for testing)"""
        cls._qry_handler = None
