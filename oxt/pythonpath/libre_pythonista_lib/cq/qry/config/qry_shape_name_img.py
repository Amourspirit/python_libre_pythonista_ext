from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_control_name_img import QryControlNameImg
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.config.qry_control_name_img import QryControlNameImg
    from libre_pythonista_lib.cq.qry.qry_t import QryT


class QryShapeNameImg(QryBase, QryT[str]):
    """
    Query that generates a shape name for an image control based on a code name.

    Inherits from QryBase and QryT[str] to provide query functionality returning a string.
    """

    def __init__(self, code_name: str) -> None:
        """
        Initialize the query with a code name.

        Args:
            code_name (str): The unique code identifier to use in the shape name
        """
        QryBase.__init__(self)
        self._code_name = code_name

    def execute(self) -> str:
        """
        Executes the query to generate the shape name.

        Returns:
            str: The generated shape name for the image control
        """
        qry = QryControlNameImg(code_name=self._code_name)
        qry_result = self._execute_qry(qry)
        return f"SHAPE_{qry_result}"
