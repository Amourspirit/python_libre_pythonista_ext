from __future__ import annotations


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.qry_t import QryT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QrySharedEvent(LogMixin, QryT):
    def __init__(self) -> None:
        LogMixin.__init__(self)
        self._kind = CalcQryKind.SIMPLE

    def execute(self) -> SharedEvent | None:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        try:
            return SharedEvent()
        except Exception:
            self.log.exception("Error getting script url")
        return None

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
