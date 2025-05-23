# region imports
from __future__ import unicode_literals, annotations
from typing import Any, Tuple, TYPE_CHECKING

import unohelper
import contextlib


from com.sun.star.task import XJob


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
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
else:
    override = lambda func: func  # noqa: E731
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader import Lo  # noqa: F401
        from ooodev.calc import CalcDoc  # noqa: F401
        from libre_pythonista_lib.doc.doc_globals import DocGlobals

# endregion imports


# region XJob
class CleanupJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.CleanupJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    # region Init

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()
        self._log.debug("init Done")

    # endregion Init

    # region execute
    @override
    def execute(self, Arguments: Any) -> None:  # type: ignore  # noqa: ANN401, N803
        self._log.debug("execute")
        try:
            # loader = Lo.load_office()
            arg1 = Arguments[0]

            for struct in arg1.Value:
                self._log.debug("Struct: %s", struct.Name)
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")
            if self.document is None:
                self._log.debug("Document is None")
                return
            run_id = self.document.RuntimeUID
            # this removes any caching for the document
            DocGlobals.delete_instance(runtime_uid=run_id)
            self._log.debug("CleanupJob complete for runtime uid: %s", run_id)

        except Exception:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="CleanupJob")

    # endregion Logging


# endregion XJob

# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*CleanupJob.get_imple())

# endregion Implementation
