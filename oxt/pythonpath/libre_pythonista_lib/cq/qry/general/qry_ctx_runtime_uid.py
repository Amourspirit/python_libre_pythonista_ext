from __future__ import annotations
from typing import Any, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.utils.result import Result


class QryCtxRuntimeUID(QryBase, QryT[Union[Result[str, None], Result[None, Exception]]]):
    """Gets the current document context runtime uid."""

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        QryBase.__init__(self)
        self._ctx = ctx

    def execute(self) -> Union[Result[str, None], Result[None, Exception]]:
        """
        Executes the query and returns the current document context runtime uid.

        Returns:
            Result: Success with str or Failure with Exception
        """
        try:
            desktop = self._ctx.getByName("/singletons/com.sun.star.frame.theDesktop")
            doc = desktop.getCurrentComponent()
            uid = doc.RuntimeUID
            return Result.success(uid)
        except Exception as e:
            return Result.failure(e)
