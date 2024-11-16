from __future__ import annotations
from typing import cast, Dict, TYPE_CHECKING
import contextlib
from pathlib import Path
import sys
from urllib.parse import parse_qs

import unohelper
from com.sun.star.task import XJobExecutor


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    this_pth = str(Path(__file__).parent.parent.parent)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    _CONDITIONS_MET = True
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override

    from ...___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ...___lo_pip___.oxt_logger.oxt_logger import OxtLogger

else:
    override = lambda func: func  # noqa: E731
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
        from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PythonEditor(unohelper.Base, XJobExecutor):
    IMPLE_NAME = "___lo_identifier___.python_editor"
    SERVICE_NAMES = ("com.sun.star.task.JobExecutor",)

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx):
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._res = ResourceResolver(self.ctx)

    @override
    def trigger(self, Event: str):
        self._log.debug(f"trigger() event: {Event}")
        if not _CONDITIONS_MET:
            return

        elif Event.startswith("py_edit_sheet&"):
            # py_edit_sheet&sheet=Sheet1&cell=A1
            try:
                self._log.debug("py_edit_sheet Event triggered")
                if TYPE_CHECKING:
                    from ...pythonpath.libre_pythonista_lib.dialog.webview.lp_py_editor.py_edit_sheet import (
                        PyEditSheet,
                    )
                else:
                    from libre_pythonista_lib.dialog.webview.lp_py_editor.py_edit_sheet import (
                        PyEditSheet,
                    )
                # _ = Lo.current_doc
                # sheet = CalcDoc.current_sheet
                args = self._convert_query_to_dict(Event.replace("py_edit_sheet&", ""))
                self._log.debug(f"args: {args}")
                sheet = cast(str, args.get("sheet"))
                cell = cast(str, args.get("cell"))
                PyEditSheet(sheet, cell).show()

            except Exception:
                self._log.exception("Error dispatching")

    def _convert_query_to_dict(self, query: str) -> Dict[str, str]:
        query_dict = parse_qs(query)
        return {k: v[0] for k, v in query_dict.items()}


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*PythonEditor.get_imple())
