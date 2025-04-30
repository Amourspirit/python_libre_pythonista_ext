from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.utils.color import Color
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.style.default_style import DefaultStyle
    from oxt.pythonpath.libre_pythonista_lib.style.style_t import StyleT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.style.default_style import DefaultStyle
    from libre_pythonista_lib.style.style_t import StyleT

    Color = int


class QryColorBgError(QryBase, QryT[Color]):
    """Gets the error control background color"""

    def __init__(self, style: StyleT | None = None) -> None:
        """Constructor

        Args:
            style (StyleT, optional): Style to use. Defaults to None.
        """
        QryBase.__init__(self)
        if style is None:
            style = DefaultStyle()
        self._style = style

    def execute(self) -> Color:
        """
        Executes the query to get error background color

        Returns:
            Color: The error background color
        """
        return self._style.color_error
