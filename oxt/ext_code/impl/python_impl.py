from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING
import contextlib
from pathlib import Path
import sys

import unohelper
from com.sun.star.task import XJobExecutor
from com.sun.star.task import XJob


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

    from oxt.___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_mgr import PyInstance
    from oxt.pythonpath.libre_pythonista_lib.log.py_logger import PyLogger

    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ooodev.exceptions.ex import CellError
    from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
    from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
    from ooo.dyn.awt.message_box_type import MessageBoxType
    from ooodev.dialog.msgbox import MsgBox
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger

else:

    def override(func):  # noqa: ANN001, ANN201
        return func

    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
        from ooodev.exceptions.ex import CellError
        from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
        from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
        from ooo.dyn.awt.message_box_type import MessageBoxType
        from ooodev.dialog.msgbox import MsgBox
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_mgr import PyInstance
        from libre_pythonista_lib.log.py_logger import PyLogger

    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PythonImpl(unohelper.Base, XJobExecutor):
    IMPLE_NAME = "___lo_identifier___.impl"
    SERVICE_NAMES = ("com.sun.star.task.JobExecutor",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._res = ResourceResolver(self.ctx)

    @override
    def trigger(self, Event: str) -> None:  # noqa: N803
        self._log.debug("trigger() event: %s", Event)
        if not _CONDITIONS_MET:
            return
        if Event == "testing":
            self._do_testing()

        elif Event == "debug_dump_module_to_log":
            self._debug_dump_module_to_log()

        elif Event == "debuggy":
            try:
                job = Lo.create_instance_mcf(XJob, "___lo_identifier___.DebugJob")
                if job is not None:
                    job.execute(())
            except Exception:
                self._log.exception("Error Starting Job")
        else:
            self._log.debug("trigger() event: %s is not known", Event)
            return

    def _debug_dump_module_to_log(self) -> None:
        doc = CalcDoc.from_current_doc()
        src = PyInstance(doc).dump_module_source_code_to_log()
        if src:
            PyLogger(doc).info(f" Source Code \n# Start Dump\n{src}\n# End Dump\n")

    def _do_testing(self) -> None:
        try:
            msg = self._res.resolve_string("title10")
            self._log.debug(msg)
            doc = CalcDoc.from_current_doc()
            sheet = doc.get_active_sheet()
            try:
                cell = sheet.get_selected_cell()
            except CellError:
                self._log.error(f"{self.__class__.__name__} - No cell selected")
                return
            # https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
            if cell.value is not None:
                msg_result = MsgBox.msgbox(
                    msg=self._res.resolve_string("mbmsg002"),
                    title=self._res.resolve_string("mbtitle002"),
                    boxtype=MessageBoxType.QUERYBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
                )
                if msg_result != MessageBoxResultsEnum.YES:
                    return
            cell.component.setFormula('=___lo_identifier___.TESTINGIMPL.TESTING(1;"$A1$1")'.upper())
            _ = cell.value
        except Exception as e:
            self._log.error(f"{self.__class__.__name__} - Error: {e}")


# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*PythonImpl.get_imple())

# endregion Implementation
