# region imports
from __future__ import unicode_literals, annotations
from typing import cast, Tuple, TYPE_CHECKING

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
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    from ooodev.utils.props import Props
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...pythonpath.libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
else:
    override = lambda func: func  # noqa: E731
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr  # noqa: F401
        from ooodev.utils.props import Props

# endregion imports


# region XJob
class PyEditCellJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.py_edit_cell_job"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx):
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Tuple[NamedValue, ...]) -> None:  # type: ignore
        global _CONDITIONS_MET
        if not _CONDITIONS_MET:
            return
        self._log.debug("execute")
        try:
            if TYPE_CHECKING:
                from ...pythonpath.libre_pythonista_lib.dialog.webview.lp_py_editor import (
                    editor,
                )  # type: ignore
            else:
                from libre_pythonista_lib.dialog.webview.lp_py_editor import editor  # type: ignore
            data_args = Props.data_to_dict(Arguments)
            self._log.debug(f"data_args: {data_args}")
            editor.main(
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

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*PyEditCellJob.get_imple())

# endregion Implementation
