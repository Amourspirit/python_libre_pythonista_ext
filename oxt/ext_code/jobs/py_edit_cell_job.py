# region imports
from __future__ import annotations
from typing import Any, cast, Tuple, TYPE_CHECKING

import unohelper
import contextlib


from com.sun.star.task import XJob
from com.sun.star.beans import NamedValue


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    # just for design time
    _CONDITIONS_MET = True
    from typing_extensions import override

    from ooodev.utils.props import Props
    from oxt.___lo_pip___.oxt_logger import OxtLogger
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.utils.props import Props

# endregion imports


# region XJob
class PyEditCellJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.py_edit_cell_job"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: object) -> None:
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Tuple[NamedValue, ...]) -> None:  # type: ignore  # noqa: N803
        global _CONDITIONS_MET
        if not _CONDITIONS_MET:
            return
        self._log.debug("execute")
        # called from dispatch/dispatch_edit_py_cell_wv.py
        try:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.dialog.webview.lp_py_editor import (
                    editor2,
                )  # type: ignore
            else:
                from libre_pythonista_lib.dialog.webview.lp_py_editor import editor2  # type: ignore
            data_args = Props.data_to_dict(Arguments)
            self._log.debug(f"data_args: {data_args}")
            editor2.main(
                sheet=cast(str, data_args.get("sheet")),
                cell=cast(str, data_args.get("cell")),
            )

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name=self.__class__.__name__)

    # endregion Logging


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*PyEditCellJob.get_imple())

# endregion Implementation
