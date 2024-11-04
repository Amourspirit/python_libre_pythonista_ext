from __future__ import annotations
from typing import cast, Sequence, Tuple, TYPE_CHECKING
import contextlib
import threading
# import time

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.task import XAsyncJob
from com.sun.star.frame import DispatchResultEvent
from com.sun.star.frame import DispatchResultState
from com.sun.star.lang import IllegalArgumentException
from com.sun.star.beans import NamedValue

from ooodev.calc import CalcDoc


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from com.sun.star.task import XJobListener
    from com.sun.star.frame import XFrame
    from ....___lo_pip___.oxt_logger import OxtLogger

    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override
else:
    override = lambda func: func  # noqa: E731
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ___lo_pip___.oxt_logger import OxtLogger


class AsyncJobImplInfo:
    """Store job related info when executeAsync() is called"""

    def __init__(
        self,
        env_type: str = "",
        event_name: str = "",
        alias: str = "",
        frame: XFrame | None = None,
        generic_config_list: str = "",
        job_config_list: str = "",
        environment_list: str = "",
        dynamic_data_list: str = "",
    ):
        self.env_type = env_type
        self.event_name = event_name
        self.alias = alias
        self.frame = frame
        self.generic_config_list = generic_config_list
        self.job_config_list = job_config_list
        self.env_list = environment_list
        self.dynamic_data_list = dynamic_data_list

    def __eq__(self, other):
        if not isinstance(other, AsyncJobImplInfo):
            return NotImplemented
        return (
            self.env_type == other.env_type
            and self.event_name == other.event_name
            and self.alias == other.alias
            and self.frame == other.frame
            and self.generic_config_list == other.generic_config_list
            and self.job_config_list == other.job_config_list
            and self.env_list == other.env_list
            and self.dynamic_data_list == other.dynamic_data_list
        )

    def __hash__(self):
        return hash(
            (
                self.env_type,
                self.event_name,
                self.alias,
                self.frame,
                self.generic_config_list,
                self.job_config_list,
                self.env_list,
                self.dynamic_data_list,
            )
        )


class HtmlPyEditor(XServiceInfo, XAsyncJob, unohelper.Base):
    IMPLE_NAME = "___lo_identifier___.AsyncJobHtmlPyEditor"
    SERVICE_NAMES = ("com.sun.star.task.AsyncJob",)

    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx):
        XServiceInfo.__init__(self)
        XAsyncJob.__init__(self)
        unohelper.Base.__init__(self)
        self._ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("HtmlPyEditor.__init__()")

    # region XAsyncJob
    @override
    def executeAsync(
        self, Arguments: Tuple[NamedValue, ...], Listener: XJobListener
    ) -> None:
        self._log.debug("HtmlPyEditor.executeAsync()")
        try:
            job_info = AsyncJobImplInfo()
            is_main_thread = threading.current_thread() is threading.main_thread()
            self._log.debug(
                f"HtmlPyEditor.executeAsync() is_main_thread: {is_main_thread}"
            )

            err = self._validate_get_info(Arguments, Listener, job_info)
            if err:
                arg_pos = 0
                if err.startswith("Listener"):
                    arg_pos = 1
                raise IllegalArgumentException(err, self, arg_pos)

            doc = CalcDoc.from_current_doc()
            sheet = doc.sheets.get_active_sheet()
            sheet["A1"].value = "HtmlPyEditor.executeAsync()"

            # self._log.debug("HtmlPyEditor.executeAsync() 1")
            # time.sleep(5)
            # self._log.debug("HtmlPyEditor.executeAsync() 2")
            # time.sleep(5)
            # self._log.debug("HtmlPyEditor.executeAsync() 3")

            is_dispatch = job_info.env_type == "DISPATCH"
            ret_val = [NamedValue()] if is_dispatch else None

            if ret_val:
                ret_val[0].Name = "SendDispatchResult"
                result_event = DispatchResultEvent()
                result_event.Source = self
                result_event.State = DispatchResultState.SUCCESS
                result_event.Result = True
                ret_val[0].Value = result_event

            self._log.debug(ret_val)
            if ret_val:
                try:
                    uno_array = uno.Any("[]com.sun.star.beans.NamedValue", ret_val)  # type: ignore
                    uno.invoke(Listener, "jobFinished", (self, uno_array))  # type: ignore
                except Exception:
                    # ensure that the job finishes otherwise the LibreOffice will hang.
                    self._log.exception("HtmlPyEditor.executeAsync() Exception")
                    Listener.jobFinished(self, None)
            else:
                Listener.jobFinished(self, None)
        except Exception as e:
            print(e)
            self._log.exception("HtmlPyEditor.executeAsync() Exception")

    # endregion XAsyncJob

    # region XServiceInfo
    @override
    def supportsService(self, ServiceName: str) -> bool:
        return ServiceName in self.SERVICE_NAMES

    @override
    def getImplementationName(self) -> str:
        return self.IMPLE_NAME

    @override
    def getSupportedServiceNames(self) -> Tuple[str, ...]:
        return self.SERVICE_NAMES

    # endregion XServiceInfo

    # region private helpers
    def _validate_get_info(
        self,
        Arguments: Tuple[NamedValue, ...],
        Listener: XJobListener,
        job_info: AsyncJobImplInfo,
    ) -> str:
        """Validate arguments and get job info"""
        if not Listener:
            return "Listener : invalid listener"

        generic_config = []
        job_config = []
        envs = []
        dynamic_data = []

        for arg in Arguments:
            if arg.Name == "Config":
                generic_config = list(arg.Value)  # type: ignore
                job_info.generic_config_list = self._format_out_args(
                    generic_config, "Config"
                )
            elif arg.Name == "JobConfig":
                job_config = list(arg.Value)  # type: ignore
                job_info.job_config_list = self._format_out_args(
                    job_config, "JobConfig"
                )
            elif arg.Name == "Environment":
                envs = list(arg.Value)  # type: ignore
                job_info.env_list = self._format_out_args(envs, "Environment")
            elif arg.Name == "DynamicData":
                dynamic_data = list(arg.Value)  # type: ignore
                job_info.dynamic_data_list = self._format_out_args(
                    dynamic_data,
                    "DynamicData",
                )

        if not envs:
            return "Args : no environment"

        for env in envs:
            if env.Name == "EnvType":
                job_info.env_type = str(env.Value)  # type: ignore
            elif env.Name == "EventName":
                job_info.event_name = str(env.Value)  # type: ignore
            elif env.Name == "Frame":
                job_info.frame = cast("XFrame", env.Value)

        if not job_info.env_type or job_info.env_type not in ["EXECUTOR", "DISPATCH"]:
            return f'Args : "{job_info.env_type}" isn\'t a valid value for EnvType'

        if generic_config:
            for cfg in generic_config:
                if cfg.Name == "Alias":
                    job_info.alias = list(cfg.Value)  # type: ignore

        return ""

    def _format_out_args(self, arg_list: Sequence[NamedValue], list_name: str) -> str:
        """Format output arguments"""
        formatted_list = f'List "{list_name}" : '
        if not arg_list:
            formatted_list += "0 items"
        else:
            formatted_list += f"{len(arg_list)} item(s) : {{ "
            for arg in arg_list:
                val = str(arg.Value)  # type: ignore
                formatted_list += f'"{arg.Name}" : "{val}", '
            formatted_list += " }"
        return formatted_list

    # endregion private helpers


g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(*HtmlPyEditor.get_imple())
