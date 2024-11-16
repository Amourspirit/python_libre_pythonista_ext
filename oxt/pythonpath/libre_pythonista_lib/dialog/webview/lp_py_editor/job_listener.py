from __future__ import annotations
from typing import Any, TYPE_CHECKING
from com.sun.star.task import XJobListener
import unohelper

if TYPE_CHECKING:
    from com.sun.star.task import XAsyncJob
    from ......___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger  # noqa: F401


class JobListener(XJobListener, unohelper.Base):
    """Job Listener for Editor Service"""

    def __init__(self, ctx: Any):
        XJobListener.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("JobListener.__init__()")

    def jobFinished(self, Job: XAsyncJob, Result: Any):
        self._log.debug("JobListener.jobFinished()")
