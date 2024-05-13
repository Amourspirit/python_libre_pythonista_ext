# region imports
from __future__ import unicode_literals, annotations
import contextlib
from typing import TYPE_CHECKING, Any, cast, Tuple
from pathlib import Path
import uno
import unohelper
import sys
import os
import time
import threading

from com.sun.star.task import XJob

if TYPE_CHECKING:
    # just for design time
    from com.sun.star.beans import NamedValue

    # from com.sun.star.lang import EventObject
    from ___lo_pip___.install.install_pkg import InstallPkg
    from ___lo_pip___.oxt_logger import OxtLogger
    from ___lo_pip___.lo_util import Session, RegisterPathKind, UnRegisterPathKind
    from ___lo_pip___.install.requirements_check import RequirementsCheck
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
else:
    RegisterPathKind = object
    UnRegisterPathKind = object


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    this_pth = os.path.dirname(__file__)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

from ___lo_pip___.dialog.handler import logger_options
from ___lo_pip___.config import Config
from ___lo_pip___.install.install_pip import InstallPip
from ___lo_pip___.lo_util.util import Util
from ___lo_pip___.adapter.top_window_listener import TopWindowListener
from ___lo_pip___.events.lo_events import LoEvents
from ___lo_pip___.events.args.event_args import EventArgs
from ___lo_pip___.events.startup.startup_monitor import StartupMonitor
from ___lo_pip___.events.named_events.startup_events import StartupNamedEvent

# endregion imports

# region Constants

implementation_name = "___lo_identifier___.___lo_implementation_name___"
implementation_services = ("com.sun.star.task.Job",)

# endregion Constants


# region XJob
class ___lo_implementation_name___(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    # region Init

    def __init__(self, ctx):
        self._this_pth = os.path.dirname(__file__)
        self._error_msg = ""
        self._job_event_name = ""
        self._valid_job_event_names = {"onFirstVisibleTask", "OnStartApp"}
        self._path_added = False
        self._added_packaging = False
        self._start_timed_out = True
        self._start_time = 0.0
        self._window_timer: threading.Timer | None = None
        self._thread_lock = threading.Lock()
        self._events = LoEvents()
        self._startup_monitor = StartupMonitor()  # start the singleton startup monitor
        # logger.debug("___lo_implementation_name___ Init")
        self.ctx = ctx
        self._user_path = ""
        self._resource_resolver: ResourceResolver | None = None
        with contextlib.suppress(Exception):
            user_path = self._get_user_profile_path(True, self.ctx)
            # logger.debug(f"Init: user_path: {user_path}")
            self._user_path = user_path

        if not TYPE_CHECKING:
            # run time
            from ___lo_pip___.lo_util import (
                Session,
                RegisterPathKind as InitRegisterPathKind,
                UnRegisterPathKind as InitUnRegisterPathKind,
            )

            global RegisterPathKind, UnRegisterPathKind
            RegisterPathKind = InitRegisterPathKind
            UnRegisterPathKind = InitUnRegisterPathKind

        self._config = Config()
        self._delay_start = self._config.delay_startup
        self._logger = self._get_local_logger()

        self._util = Util()
        self._logger.debug("Got OxtLogger instance")

        # create an environment variable for the log file path.
        # This is used to give end users another way to find the log file via python.
        # Environment variable something like: ORG_OPENOFFICE_EXTENSIONS_OOOPIP_LOG_FILE, this will change for your extension.
        # The variable is determined by the lo_identifier in the pyproject.toml file, tool.oxt.token section.
        # To get the log file path in python: os.environ["ORG_OPENOFFICE_EXTENSIONS_OOOPIP_LOG_FILE"]
        # A Log file will only be created if log_file is set and log_level is not NONE, set in pyproject.toml file, tool.oxt.token section.
        if self._logger.log_file:
            log_env_name = self._config.lo_identifier.upper().replace(".", "_") + "_LOG_FILE"
            self._logger.debug(f"Log Path Environment Name: {log_env_name}")
            os.environ[log_env_name] = self._logger.log_file

        self._session = Session()
        self._logger.debug("___lo_implementation_name___ Init Done")

        self._add_py_req_pkgs_to_sys_path()
        if not TYPE_CHECKING:
            # run time
            # must be after self._add_py_req_pkgs_to_sys_path()
            try:
                from ___lo_pip___.install.requirements_check import RequirementsCheck
            except Exception as err:
                self._logger.error(err, exc_info=True)
        self._requirements_check = RequirementsCheck()
        self._add_site_package_dir_to_sys_path()
        self._init_isolated()

    # endregion Init

    # region execute
    def execute(self, *args: Tuple[NamedValue, ...]) -> None:
        # make sure our pythonpath is in sys.path
        self._start_time = time.time()
        self._logger.debug("___lo_implementation_name___ executing")
        try:
            self._job_event_name = self._get_event_name(args)
        except Exception as err:
            self._logger.error(err, exc_info=True)
            self._job_event_name = ""
        if not self._is_valid_job_event():
            self._logger.error(f"Invalid job event name: {self._job_event_name}")
            self._logger.info(f"Valid job event names: {self._valid_job_event_names}")
            return
        self._logger.debug(f"Job event name: {self._job_event_name}")
        try:
            self._add_py_pkgs_to_sys_path()
            self._add_py_req_pkgs_to_sys_path()
            self._add_pure_pkgs_to_sys_path()

            if self._config.log_level < 20:  # Less than INFO
                self._show_extra_debug_info()
                # self._config.extension_info.log_extensions(self._logger)

            requirements_met = False
            if self._requirements_check.check_requirements() is True and not self._config.has_locals:
                requirements_met = True

            if requirements_met:
                self._logger.debug("Requirements are met. Nothing more to do.")
                self._log_ex_time(self._start_time)
                return

            if self._config.py_pkg_dir:
                # add package zip file to the sys.path
                pth = os.path.join(os.path.dirname(__file__), f"{self._config.py_pkg_dir}.zip")

                if os.path.exists(pth) and os.path.isfile(pth) and os.path.getsize(pth) > 0 and pth not in sys.path:
                    self._logger.debug(f"sys.path appended: {pth}")
                    sys.path.append(pth)

            if not self.has_internet_connection:
                self._logger.error("No internet connection")
                with contextlib.suppress(Exception):
                    self._error_msg = self.resource_resolver.resolve_string("msg07")

            if self._delay_start:

                def _on_window_opened(source: Any, event_args: EventArgs, *args, **kwargs) -> None:
                    self.on_window_opened(source=source, event_args=event_args, *args, **kwargs)

                self._fn_on_window_opened = _on_window_opened

                self._twl = TopWindowListener()
                self._start_window_timer()
                self._twl.on("windowOpened", _on_window_opened)

        except Exception as err:
            if self._logger:
                self._logger.error(err)
            self._log_ex_time(self._start_time)
            return
        finally:
            # self._remove_local_path_from_sys_path()
            self._remove_py_req_pkgs_from_sys_path()
        if self._delay_start:
            return
        self._real_execute(start_time=self._start_time, has_window=False)

    def _real_execute(self, start_time: float, has_window: bool = False) -> None:
        if has_window:
            # LibreOffice runs extension in parallel, so we need to wait in line
            wait_count = 0
            while os.environ.get("OOOPIP_RUNNER_WAIT_IN_LINE", ""):
                wait_count += 1
                if wait_count == 1:
                    self._logger.info("Waiting in line. Other Installers are working...")
                time.sleep(0.5)
            if wait_count > 0:
                # reset the time and don't include wait time.
                start_time = time.time()
                self._logger.info("Done waiting in line.")
            else:
                self._logger.debug("No other Installers are running. Starting...")

        try:
            with self._thread_lock:
                os.environ["OOOPIP_RUNNER_WAIT_IN_LINE"] = "1"
            if not TYPE_CHECKING:
                # run time
                self._logger.debug("Imported InstallPip")
                from ___lo_pip___.install.install_pkg import InstallPkg
            pip_installer = InstallPip(self.ctx)
            self._logger.debug("Created InstallPip instance")
            if pip_installer.is_pip_installed():
                self._logger.info("Pip is already installed")
            else:
                self._logger.info("Pip is not installed. Attempting to install")
                if not pip_installer.is_internet:
                    self._logger.error("No internet connection!")
                    return
                pip_installer.install_pip()
                if pip_installer.is_pip_installed():
                    self._logger.info("Pip has been installed")
                else:
                    self._logger.info("Pip was not successfully installed")
                    return

            # install wheel if needed
            self._install_wheel()

            # install any packages that are not installed
            if self._config.has_locals:
                self._install_locals()
            pkg_installer = InstallPkg(ctx=self.ctx)
            self._logger.debug("Created InstallPkg instance")
            pkg_installer.install()

            self._post_install()

            if has_window:
                self._display_complete_dialog()

            self._logger.info(f"{self._config.lo_implementation_name} execute Done!")
        except Exception as err:
            if self._logger:
                self._logger.error(err)
        finally:
            # self._remove_local_path_from_sys_path()
            with self._thread_lock:
                del os.environ["OOOPIP_RUNNER_WAIT_IN_LINE"]
            self._remove_py_req_pkgs_from_sys_path()
            self._log_ex_time(start_time)

    # endregion execute

    # region Destructor
    def __del__(self):
        if self._added_packaging and "packaging" in sys.modules:
            del sys.modules["packaging"]
        if "___lo_pip___" in sys.modules:
            # clean up by removing the ___lo_pip___ module from sys.modules
            # module still can be imported if needed.
            del sys.modules["___lo_pip___"]

    # endregion Destructor

    # region Install

    def _install_wheel(self) -> None:
        if not self._config.install_wheel:
            self._logger.debug("Install wheel is set to False. Skipping wheel installation.")
            return
        self._logger.debug("Install wheel is set to True. Installing wheel.")
        try:
            from ___lo_pip___.install.extras.install_wheel import InstallWheel

            installer = InstallWheel(ctx=self.ctx)
            installer.install()
        except Exception as err:
            self._logger.error(f"Unable to install wheel: {err}", exc_info=True)
            return
        self._logger.debug("Install wheel done.")

    # endregion Install

    # region Register/Unregister sys paths

    def _add_py_pkgs_to_sys_path(self) -> None:
        pth = Path(os.path.dirname(__file__), f"{self._config.py_pkg_dir}.zip")
        if not pth.exists():
            return
        result = self._session.register_path(pth, True)
        self._log_sys_path_register_result(pth, result)

    def _add_pure_pkgs_to_sys_path(self) -> None:
        pth = Path(os.path.dirname(__file__), "pure.zip")
        if not pth.exists():
            self._logger.debug("pure.zip not found.")
            return
        result = self._session.register_path(pth, True)
        self._log_sys_path_register_result(pth, result)

    def _add_py_req_pkgs_to_sys_path(self) -> None:
        pth = Path(os.path.dirname(__file__), f"req_{self._config.py_pkg_dir}.zip")
        if not pth.exists():
            return
        # should be only LibreOffice on Windows needs packaging
        try:
            self._logger.debug("Importing packaging")
            import packaging  # noqa: F401

            self._logger.debug("packaging imported")
        except ModuleNotFoundError:
            self._logger.debug("packaging not found. Adding to sys.path")
            result = self._session.register_path(pth, True)
            self._log_sys_path_register_result(pth, result)
            if result == RegisterPathKind.REGISTERED:
                self._added_packaging = True

    def _remove_py_req_pkgs_from_sys_path(self) -> None:
        pth = Path(os.path.dirname(__file__), f"req_{self._config.py_pkg_dir}.zip")
        result = self._session.unregister_path(pth)
        self._log_sys_path_unregister_result(pth, result)

    def _add_site_package_dir_to_sys_path(self) -> None:
        if self._config.is_shared_installed or self._config.is_bundled_installed:
            self._logger.debug("All users, not adding site-packages to sys.path")
            return
        if not self._config.site_packages:
            return
        result = self._session.register_path(self._config.site_packages, True)
        self._log_sys_path_register_result(self._config.site_packages, result)

    def _log_sys_path_register_result(self, pth: Path | str, result: RegisterPathKind) -> None:
        if not isinstance(pth, str):
            pth = str(pth)
        if result == RegisterPathKind.NOT_REGISTERED:
            if not pth:
                self._logger.debug("Path not registered. Can't register empty string")
            else:
                self._logger.debug(f"Path Not Registered, unknown reason: {pth}")
        elif result == RegisterPathKind.ALREADY_REGISTERED:
            self._logger.debug(f"Path already registered: {pth}")
        else:
            self._logger.debug(f"Path registered: {pth}")

    def _log_sys_path_unregister_result(self, pth: Path | str, result: UnRegisterPathKind) -> None:
        if not isinstance(pth, str):
            pth = str(pth)
        if result == UnRegisterPathKind.NOT_UN_REGISTERED:
            if not pth:
                self._logger.debug("Path not unregistered. Can't unregister empty string")
            else:
                self._logger.debug(f"Path Not unregistered, unknown reason: {pth}")
        elif result == UnRegisterPathKind.ALREADY_UN_REGISTERED:
            self._logger.debug(f"Path already unregistered: {pth}")
        else:
            self._logger.debug(f"Path unregistered: {pth}")

    # endregion Register/Unregister sys paths

    # region other methods

    def on_window_opened(self, source: Any, event_args: EventArgs, *args, **kwargs) -> None:
        """is invoked when a LibreOffice top window is activated."""
        if self._twl is None:
            return
        self._start_timed_out = False
        if self._window_timer:
            # if we got to here then the timer is no longer needed
            self._logger.debug("Stopping timer")
            self._window_timer.cancel()
        self._logger.debug("Window Opened Event took place.")
        # event = cast("EventObject", event_args.event_data)
        # self._logger.debug(dir(event.Source))
        self._twl = None
        self._fn_on_window_opened = None
        self._events.trigger(StartupNamedEvent.WINDOW_STARTED, EventArgs(self))
        if self._error_msg:
            with contextlib.suppress(Exception):
                title = self.resource_resolver.resolve_string("title01") or self._config.lo_implementation_name
                self._display_message(msg=self._error_msg, title=title, suppress_error=False)
            return
        self._ex_thread = threading.Thread(target=self._real_execute, args=(self._start_time, True))
        self._ex_thread.start()
        # self._real_execute()

    def _start_window_timer(self) -> None:
        """Starts the timer to delay the execution of the execute method."""

        def timer_tick() -> None:
            self._logger.debug("Window timer elapsed.")
            if self._start_timed_out:
                self._logger.debug("Window timed out. Starting execute.")
                t = threading.Thread(target=self._real_execute)
                t.start()
            else:
                self._logger.debug("Window opened and did not time out. Not starting execute.")

        self._logger.debug("Starting timer")
        self._fn_timer_tick = timer_tick  # keep alive
        self._delay_start = True
        self._window_timer = threading.Timer(self._config.window_timeout, timer_tick)
        self._window_timer.start()

    def _get_event_name(self, args: Tuple[Tuple[NamedValue, ...], ...]) -> str:
        """
        Gets the event name from the args.

        Args:
            args (Tuple[Tuple[NamedValue, ...], ...]): Event args passed to execute.

        Returns:
            str: Event name.
        """
        if not args:
            return ""
        for tup in args:
            if not tup:
                continue
            for arg in tup:
                if arg.Name != "Environment":
                    continue
                named_vals = cast(Tuple["NamedValue", ...], arg.Value)
                for val in named_vals:
                    if val.Name == "EventName":
                        return str(val.Value)
        return ""

    def _is_valid_job_event(self) -> bool:
        return self._job_event_name in self._valid_job_event_names

    def _display_message(self, msg: str, title: str = "Message", suppress_error: bool = False) -> None:
        try:
            from ___lo_pip___.dialog.message_dialog import MessageDialog

            ctx = uno.getComponentContext()

            if tk := ctx.ServiceManager.createInstance("com.sun.star.awt.Toolkit"):  # type: ignore
                top_win = tk.getTopWindow(0)
            else:
                top_win = None
            msg_box = MessageDialog(ctx=self.ctx, parent=top_win, message=msg, title=title)  # type: ignore
            _ = msg_box.execute()
        except Exception as err:
            if not suppress_error:
                self._logger.error(err, exc_info=True)

    def _display_complete_dialog(self) -> None:
        if not self._config.show_progress:
            return
        try:
            from ___lo_pip___.dialog.count_down_dialog import CountDownDialog

            msg = self.resource_resolver.resolve_string("msg06")
            title = self.resource_resolver.resolve_string("title01") or self._config.lo_implementation_name
            dlg = CountDownDialog(msg=msg, title=title, display_time=5)
            dlg.start()
        except Exception as err:
            self._logger.error(err, exc_info=True)

    def _log_ex_time(self, start_time: float, msg: str = "") -> None:
        if not self._logger:
            return
        end_time = time.time()
        total_time = end_time - start_time
        self._logger.info(f"{self._config.lo_implementation_name} execution time: {total_time:.3f} seconds")

    def _get_user_profile_path(self, as_sys_path: bool = True, ctx: Any = None) -> str:
        """
        Returns the path to the user profile directory.

        Args:
            as_sys_path (bool): If True, returns the path as a system path entry otherwise ``file:///`` format.
                Defaults to True.
        """
        if ctx is None:
            ctx = uno.getComponentContext()
        result = ctx.ServiceManager.createInstance(
            "com.sun.star.util.PathSubstitution"
        ).substituteVariables(  # type: ignore
            "$(user)", True
        )
        return uno.fileUrlToSystemPath(result) if as_sys_path else result

    # endregion other methods

    # region install local
    def _install_locals(self) -> None:
        """Pip installs any ``.whl`` or ``.tar.gz`` files in the ``locals`` directory."""
        if not self._config.has_locals:
            self._logger.debug("Install local is set to False. Skipping local installation.")
            return
        self._logger.debug("Install local is set to True. Installing local packages.")
        try:
            from ___lo_pip___.install.install_pkg_local import InstallPkgLocal

            installer = InstallPkgLocal(ctx=self.ctx)
            _ = installer.install()
        except Exception as err:
            self._logger.error(f"Unable to install local packages: {err}", exc_info=True)
            return
        self._logger.debug("Install local done.")

    # endregion install local

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger

        # if self._user_path:
        #     log_file = os.path.join(self._user_path, "py_runner.log")
        #     return OxtLogger(log_file=log_file, log_name=__name__)
        return OxtLogger(log_name=__name__)

    # endregion Logging

    # region Post Install
    def _post_install(self) -> None:
        self._logger.debug("Post Install starting")
        if not self._config.sym_link_cpython:
            self._logger.debug(
                "Not creating CPython link because configuration has it turned off. Skipping post install."
            )
            return
        if not self._config.is_mac and not self._config._is_app_image:
            self._logger.debug("Not Mac or AppImage. Skipping post install.")
            return
        try:
            from ___lo_pip___.install.post.cpython_link import CPythonLink

            link = CPythonLink()
            link.link()
        except Exception as err:
            self._logger.error(err, exc_info=True)
            return
        self._logger.debug("Post Install Done")

    # endregion Post Install

    # region Isolate
    def _init_isolated(self) -> None:
        if not self._config.is_win:
            self._logger.debug("Not Windows, not isolating")
            return

        from ___lo_pip___.lo_util.target_path import TargetPath

        target_path = TargetPath()
        if target_path.has_other_target:
            target_path.ensure_exist()
        if target_path.exist():
            result = self._session.register_path(target_path.target, True)
            self._log_sys_path_register_result(target_path.target, result)

    # endregion Isolate

    # region Debug

    def _show_extra_debug_info(self):
        self._logger.debug(f"Config Package Location: {self._config.package_location}")
        self._logger.debug(f"Config Python Path: {self._config.python_path}")
        self._logger.debug(f"Config Site Packages Path: {self._config.site_packages}")
        self._logger.debug(f"Config Is User Installed: {self._config.is_user_installed}")
        self._logger.debug(f"Config Is Share Installed: {self._config.is_shared_installed}")
        self._logger.debug(f"Config Is Bundle Installed: {self._config.is_bundled_installed}")

        self._logger.debug(f"Session - LibreOffice Share: {self._session.share}")
        self._logger.debug(f"Session - LibreOffice Share Python: {self._session.shared_py_scripts}")
        self._logger.debug(f"Session - LibreOffice Share Scripts: {self._session.shared_scripts}")
        self._logger.debug(f"Session - LibreOffice Username: {self._session.user_name}")
        self._logger.debug(f"Session - LibreOffice User Profile: {self._session.user_profile}")
        self._logger.debug(f"Session - LibreOffice User Scripts: {self._session.user_scripts}")

        self._logger.debug(f"Util.config - Module: {self._util.config('Module')}")
        self._logger.debug(f"Util.config - UserConfig: {self._util.config('UserConfig')}")
        self._logger.debug(f"Util.config - Config: {self._util.config('Config')}")
        self._logger.debug(f"Util.config - BasePathUserLayer: {self._util.config('BasePathUserLayer')}")
        self._logger.debug(f"Util.config - BasePathShareLayer: {self._util.config('BasePathShareLayer')}")

    # endregion Debug

    # region Properties
    @property
    def resource_resolver(self) -> ResourceResolver:
        if self._resource_resolver is None:
            from ___lo_pip___.lo_util.resource_resolver import ResourceResolver

            self._resource_resolver = ResourceResolver(self.ctx)
        return self._resource_resolver

    @property
    def has_internet_connection(self) -> bool:
        try:
            return self._has_internet_connection
        except AttributeError:
            from ___lo_pip___.install.download import Download

            self._has_internet_connection = Download().is_internet
        return self._has_internet_connection

    # endregion Properties


# endregion XJob

# region Implementation

g_TypeTable = {}
# python loader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()

# add the FormatFactory class to the implementation container,
# which the loader uses to register/instantiate the component.
g_ImplementationHelper.addImplementation(___lo_implementation_name___, implementation_name, implementation_services)

g_ImplementationHelper.addImplementation(
    logger_options.OptionsDialogHandler, logger_options.IMPLEMENTATION_NAME, (logger_options.IMPLEMENTATION_NAME,)
)

# uncomment here and int options.xcu to use the example dialog
# from ___lo_pip___.dialog.handler import example

# g_ImplementationHelper.addImplementation(
#     example.OptionsDialogHandler, example.IMPLEMENTATION_NAME, (example.IMPLEMENTATION_NAME,)
# )

# endregion Implementation
