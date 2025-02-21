from __future__ import annotations
from typing import Any, Type, Tuple, cast, TYPE_CHECKING
from pathlib import Path
import contextlib
import sys
import unohelper
from com.github.amourspirit.extensions.librepythonista import XPy2  # type: ignore


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    # this_pth = os.path.dirname(__file__)
    this_pth = str(Path(__file__).parent.parent.parent)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from com.sun.star.frame import Desktop
    from ooodev.calc import CalcDoc
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_init import DocInit

    break_mgr = BreakMgr()
else:
    _CONDITIONS_MET = _conditions_met()

    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ___lo_pip___.debug.break_mgr import BreakMgr
        from libre_pythonista_lib.doc.doc_init import DocInit

        # Initialize the breakpoint manager
        break_mgr = BreakMgr()
        # break_mgr.add_breakpoint("librepythonista.PyImpl2.matched_rule")
        # break_mgr.add_breakpoint("librepythonista.PyImpl2.pyc")
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PyImpl2(unohelper.Base, XPy2):
    IMPLE_NAME = "___lo_identifier___.PyImpl2"
    SERVICE_NAMES = ("com.sun.star.sheet.AddIn",)

    @classmethod
    def get_imple(cls) -> Tuple[Type[PyImpl2], str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        # this is only init one time per session. When a new document is loaded, it is not called.
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Pyc2: PyImpl init")
        try:
            mgr = self.ctx.getServiceManager()
            self.desktop = cast(
                "Desktop",
                mgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx),
            )
        except Exception as e:
            self._log.error(f"Error: {e}", exc_info=True)

        # it seems init is only call when the functions is first called.

    def pyc2(self, sheet_num: int, cell_address: str, *args) -> Any:  # noqa: ANN002, ANN401
        if not _CONDITIONS_MET:
            self._log.error("pyc2 - Conditions not met")
            return None  # type: ignore
        self._log.debug("pyc2 entered")

        break_mgr.check_breakpoint("librepythonista.PyImpl2.pyc")

        try:
            # CalcDoc.from_current_doc() should not be used here.
            # It will return the previous active document if this document is not yet ready.
            # This will cause the code to run on the wrong document.
            # This only happens when a current Calc Document is open and an existing doc is opened via File -> Open.
            # Even then it is only an issue while the document is opening.
            # However that issue cause the popup dialog to be displayed one time for each formula.
            # Getting the document from this desktop solve this issue. Mainly because the controller is None when the document is not ready.
            frame = self.desktop.getActiveFrame()
            controller = frame.getController()
            model = controller.getModel()
            # self._logger.debug(f"pyc - Doc UID: {model.RuntimeUID}")
            doc = CalcDoc.get_doc_from_component(model)
        except Exception:
            self._log.warning(
                "pyc - Could not get current document. This usually happens when the document is not fully loaded."
            )
            return None

        try:
            doc_init = DocInit(doc=doc)  # singleton
            doc_init.ensure_doc_init()
            doc_init.ensure_sheet_init(doc.get_sheet(sheet_num - 1))
        except Exception as e:
            self._log.exception("Error Init Doc: %s", e)

        self._log.debug("pyc2 - Doc UID: %s", doc.runtime_uid)
        result = (("pyc2",),)
        self._log.debug("pyc2 - Done")
        return result


g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*PyImpl2.get_imple())
