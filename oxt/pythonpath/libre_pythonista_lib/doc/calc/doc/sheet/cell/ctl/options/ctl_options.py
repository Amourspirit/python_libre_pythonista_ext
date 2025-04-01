from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.style.default_style import DefaultStyle
    from oxt.pythonpath.libre_pythonista_lib.style.style_t import StyleT
else:
    from libre_pythonista_lib.style.default_style import DefaultStyle
    from libre_pythonista_lib.style.style_t import StyleT


class CtlOptions:
    """Options for a cell control."""

    def __init__(self, *, style: StyleT | None = None) -> None:
        """Constructor

        Args:
            style (StyleT, optional): Style to use. Defaults to None.
        """
        if style is None:
            style = DefaultStyle()
        self._style = style

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}()>"

    @property
    def style(self) -> StyleT:
        """Gets/Sets the style"""
        return self._style

    @style.setter
    def style(self, value: StyleT) -> None:
        self._style = value
