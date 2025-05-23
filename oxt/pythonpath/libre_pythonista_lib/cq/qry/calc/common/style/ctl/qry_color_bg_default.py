from __future__ import annotations
from typing import TYPE_CHECKING, Union


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


class QryColorBgDefault(QryBase, QryT[Color]):
    """Gets the default control background color"""

    def __init__(self, style: Union[StyleT, None] = None) -> None:
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
        Executes the query to get default background color

        Returns:
            Color: The default background color
        """
        return self._style.color_main
