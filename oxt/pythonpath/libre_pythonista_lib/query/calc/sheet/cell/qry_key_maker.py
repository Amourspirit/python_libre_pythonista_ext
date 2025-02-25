from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
else:
    from libre_pythonista_lib.query.qry_base import QryBase
    from libre_pythonista_lib.query.qry_t import QryT
    from libre_pythonista_lib.cell.props.key_maker import KeyMaker


class QryKeyMaker(QryBase, QryT[KeyMaker]):
    """Gets the KeyMaker singleton"""

    def __init__(self) -> None:
        QryBase.__init__(self)

    def execute(self) -> KeyMaker:
        """
        Executes the query and gets the KeyMaker singleton.

        Returns:
            KeyMaker: The KeyMaker singleton.
        """

        return KeyMaker()
