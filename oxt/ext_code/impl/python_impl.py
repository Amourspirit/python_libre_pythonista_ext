from __future__ import annotations
from typing import TYPE_CHECKING
import contextlib
from pathlib import Path
import sys

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
    from ...pythonpath.libre_pythonista_lib.code.py_source_mgr import PyInstance
    from ...pythonpath.libre_pythonista_lib.log.py_logger import PyLogger
    from ...pythonpath.libre_pythonista_lib import wv

    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ooodev.exceptions.ex import CellError
    from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
    from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
    from ooo.dyn.awt.message_box_type import MessageBoxType
    from ooodev.dialog.msgbox import MsgBox
    from ...___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ...pythonpath.libre_pythonista_lib.const import (
        UNO_DISPATCH_ABOUT,
        UNO_DISPATCH_LOG_WIN,
        FORMULA_PYC,
        UNO_DISPATCH_PIP_PKG_INSTALL,
        UNO_DISPATCH_PIP_PKG_UNINSTALL,
        UNO_DISPATCH_PIP_PKG_INSTALLED,
        UNO_DISPATCH_PIP_PKG_LINK,
        UNO_DISPATCH_PIP_PKG_UNLINK,
        UNO_DISPATCH_PYC_FORMULA,
        UNO_DISPATCH_PYC_FORMULA_DEP,
    )
else:
    override = lambda func: func
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
        from ooodev.exceptions.ex import CellError
        from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
        from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
        from ooo.dyn.awt.message_box_type import MessageBoxType
        from ooodev.dialog.msgbox import MsgBox
        from libre_pythonista_lib.code.py_source_mgr import PyInstance
        from libre_pythonista_lib.log.py_logger import PyLogger
        from libre_pythonista_lib import wv
        from libre_pythonista_lib.const import (
            UNO_DISPATCH_ABOUT,
            UNO_DISPATCH_LOG_WIN,
            FORMULA_PYC,
            UNO_DISPATCH_PIP_PKG_INSTALL,
            UNO_DISPATCH_PIP_PKG_UNINSTALL,
            UNO_DISPATCH_PIP_PKG_INSTALLED,
            UNO_DISPATCH_PIP_PKG_LINK,
            UNO_DISPATCH_PIP_PKG_UNLINK,
            UNO_DISPATCH_PYC_FORMULA,
            UNO_DISPATCH_PYC_FORMULA_DEP,
        )

    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PythonImpl(unohelper.Base, XJobExecutor):
    IMPLE_NAME = "___lo_identifier___.impl"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

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
        if Event == "testing":
            self._do_testing()
        elif Event == "pyc_formula_with_dependent":
            try:
                self._log.debug(f"PYC Formula with dependent, Dispatching {UNO_DISPATCH_PYC_FORMULA_DEP}")
                _ = Lo.current_doc
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_PYC_FORMULA_DEP)
                self._log.debug(f"PYC Formula with dependent, Dispatched {UNO_DISPATCH_PYC_FORMULA_DEP}")
            except Exception as e:
                self._log.exception(f"Error dispatching")

        elif Event == "debug_dump_module_to_log":
            self._debug_dump_module_to_log()
        elif Event == "about":
            try:
                self._log.debug(f"About, Dispatching {UNO_DISPATCH_ABOUT}")
                _ = Lo.current_doc
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_ABOUT)
                self._log.debug(f"About, Dispatched {UNO_DISPATCH_ABOUT}")
            except Exception as e:
                self._log.exception(f"Error dispatching")
        elif Event == "install_pip_pkg":
            try:
                self._log.debug(f"Install Pkg, Dispatching {UNO_DISPATCH_PIP_PKG_INSTALL}")
                _ = Lo.current_doc
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_PIP_PKG_INSTALL)
                self._log.debug(f"Install Pkg, Dispatched {UNO_DISPATCH_PIP_PKG_INSTALL}")
            except Exception as e:
                self._log.exception(f"Error dispatching")
        elif Event == "uninstall_pip_pkg":
            try:
                self._log.debug(f"Installed Pkg, Dispatching {UNO_DISPATCH_PIP_PKG_UNINSTALL}")
                _ = Lo.current_doc
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_PIP_PKG_UNINSTALL)
                self._log.debug(f"Installed Pkg, Dispatched {UNO_DISPATCH_PIP_PKG_UNINSTALL}")
            except Exception as e:
                self._log.exception(f"Error dispatching")
        elif Event == "installed_pip_pkg":
            try:
                self._log.debug(f"Installed Pkg, Dispatching {UNO_DISPATCH_PIP_PKG_INSTALLED}")
                _ = Lo.current_doc
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_PIP_PKG_INSTALLED)
                self._log.debug(f"Installed Pkg, Dispatched {UNO_DISPATCH_PIP_PKG_INSTALLED}")
            except Exception as e:
                self._log.exception(f"Error dispatching")

        elif Event == "log_window":
            try:
                self._log.debug(f"Log Window, Dispatching {UNO_DISPATCH_LOG_WIN}")
                _ = Lo.current_doc
                # in_thread=1 to wait for thread to join else thread is not joined.
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_LOG_WIN + "?in_thread=0", in_thread=True)
                self._log.debug(f"Log Window, Dispatched {UNO_DISPATCH_LOG_WIN}")
            except Exception:
                self._log.exception(f"Error dispatching")
        elif Event == "link_python":
            try:
                self._log.debug(f"Dispatching {UNO_DISPATCH_PIP_PKG_LINK}")
                _ = Lo.current_doc
                # in_thread=1 to wait for thread to join else thread is not joined.
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_PIP_PKG_LINK)
                self._log.debug(f"Dispatched {UNO_DISPATCH_PIP_PKG_LINK}")
            except Exception:
                self._log.exception(f"Error dispatching")
        elif Event == "unlink_python":
            try:
                self._log.debug(f"Dispatching {UNO_DISPATCH_PIP_PKG_UNLINK}")
                _ = Lo.current_doc
                # in_thread=1 to wait for thread to join else thread is not joined.
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_PIP_PKG_UNLINK)
                self._log.debug(f"Dispatched {UNO_DISPATCH_PIP_PKG_UNLINK}")
            except Exception:
                self._log.exception(f"Error dispatching")
        # elif Event == "wv":
        #     try:
        #         wv.main()
        #     except Exception:
        #         self._log.exception(f"Error importing wv")
        else:
            try:
                self._log.debug(f"PYC Formula, Dispatching {UNO_DISPATCH_PYC_FORMULA}")
                _ = Lo.current_doc
                Lo.dispatch_cmd(cmd=UNO_DISPATCH_PYC_FORMULA)
                self._log.debug(f"PYC Formula, Dispatched {UNO_DISPATCH_PYC_FORMULA}")
            except Exception as e:
                self._log.exception(f"Error dispatching")

    def _debug_dump_module_to_log(self) -> None:
        doc = CalcDoc.from_current_doc()
        src = PyInstance(doc).dump_module_source_code_to_log()
        if src:
            PyLogger(doc).info(f" Source Code \n# Start Dump\n{src}\n# End Dump\n")

    def _do_testing(self):
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


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(*PythonImpl.get_imple())
