from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
else:
    from libre_pythonista_lib.query.qry_t import QryT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cell.props.key_maker import KeyMaker


class QryKeyMaker(QryT[KeyMaker]):
    """Gets the KeyMaker singleton"""

    def __init__(self) -> None:
        self._kind = CalcQryKind.SIMPLE

    def execute(self) -> KeyMaker:
        """
        Executes the query and gets the KeyMaker singleton.

        Returns:
            KeyMaker: The KeyMaker singleton.
        """

        return KeyMaker()

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
