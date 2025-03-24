from __future__ import annotations

from typing import TYPE_CHECKING

from ooodev.utils.color import StandardColor

if TYPE_CHECKING:
    from ooodev.utils.color import Color
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT

    Color = int


class QryColorBgError(QryBase, QryT[Color]):
    """Gets the error control background color"""

    def __init__(self) -> None:
        QryBase.__init__(self)

    def execute(self) -> Color:
        """
        Executes the query to get error background color

        Returns:
            Color: The error background color
        """
        return StandardColor.RED_LIGHT3
