from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING, Optional
import threading
import time

from ooodev.loader import Lo
from ooodev.dialog.msgbox import (
    MessageBoxType,
    MsgBox,
    MessageBoxButtonsEnum,
    MessageBoxResultsEnum,
)

# from ..dialog.user_input.input import Input

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ....___lo_pip___.config import Config
    from ....___lo_pip___.install.post.cpython_link import CPythonLink
    from ....___lo_pip___.events.lo_events import LoEvents
    from ....___lo_pip___.events.args.event_args import EventArgs
    from ....___lo_pip___.events.named_events import GenNamedEvent
    from ....___lo_pip___.install.progress_window.progress_dialog_true import (
        ProgressDialogTrue,
    )
    from ....___lo_pip___.install.progress import Progress
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ___lo_pip___.install.post.cpython_link import CPythonLink
    from ___lo_pip___.events.lo_events import LoEvents
    from ___lo_pip___.events.args.event_args import EventArgs
    from ___lo_pip___.events.named_events import GenNamedEvent
    from ___lo_pip___.install.progress_window.progress_dialog_true import (
        ProgressDialogTrue,
    )
    from ___lo_pip___.install.progress import Progress


class Linking:
    def __init__(self) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._ctx = Lo.get_context()
        self._rr = ResourceResolver(self._ctx)
        self._config = Config()
        self._cp = CPythonLink()
        self._events = LoEvents()
        self._init_events()

    def _init_events(self) -> None:
        # By default no progress window will be displayed without this rule.
        # The display window is part of the original install process
        # and does not contains a rule that checks if the window is available.
        # This class is expected to be called only from the main window via dispatch command.
        # By hooking the event we can add the rule to the list of rules that will be checked.
        # This will allow a dialog progress window to be displayed.
        self._fn_on_progress_rules_event = self._on_progress_rules_event
        self._events.on(GenNamedEvent.PROGRESS_RULES_EVENT, self._fn_on_progress_rules_event)

    def _on_progress_rules_event(self, args: Any, event_arg: EventArgs) -> None:  # noqa: ANN401
        # add the ProgressDialogTrue rule to the rules list to get the progress dialog to display
        d_args = cast(Dict[str, Any], event_arg.event_data)
        rules = cast(list, d_args["rules"])
        rules.append(ProgressDialogTrue)

    def is_linking_needed(self) -> bool:
        """
        Check if linking is needed.
        """
        return self._cp.get_needs_linking()

    def link(self) -> None:
        """
        Link the files.
        """
        if not self.is_linking_needed():
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg012"),  # No Linking need on this installation of LibreOffice
                title=self._rr.resolve_string("mbtitle012"),  # No Links
                boxtype=MessageBoxType.INFOBOX,
            )
            return
        msg_result = MsgBox.msgbox(
            self._rr.resolve_string(
                "mbmsg014"
            ),  # Are you sure? This may cause the extension to stop working properly!
            title=self._rr.resolve_string("title14"),  # Confirm
            boxtype=MessageBoxType.QUERYBOX,
            buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
        )
        if msg_result != MessageBoxResultsEnum.YES:
            return
        thread = threading.Thread(target=self._link_worker, args=(), daemon=True)
        thread.start()

    def unlink(self) -> None:
        """
        Removes all symlinks that match the current suffix.
        """
        if not self.is_linking_needed():
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg012"),  # No Linking need on this installation of LibreOffice
                title=self._rr.resolve_string("mbtitle012"),  # No Links
                boxtype=MessageBoxType.INFOBOX,
            )
            return
        msg_result = MsgBox.msgbox(
            self._rr.resolve_string(
                "mbmsg013"
            ),  # Are you sure? This may cause the extension to stop working properly!
            title=self._rr.resolve_string("title14"),  # Confirm
            boxtype=MessageBoxType.QUERYBOX,
            buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
        )
        if msg_result != MessageBoxResultsEnum.YES:
            return
        thread = threading.Thread(target=self._unlink_worker, args=(), daemon=True)
        thread.start()

    def _link_worker(self) -> None:
        """
        Removes all symlinks that match the current suffix.
        """
        start_time = time.time()
        progress: Optional[Progress] = None
        try:
            if self._config.show_progress:
                msg = self._rr.resolve_string("msg20")
                title = msg
                progress = Progress(start_msg=msg, title=title)
                progress.start()
            self._cp.link()
        except Exception as err:
            self._log.error(err, exc_info=True)
            return
        finally:
            if progress:
                # keep the progress window open for at least 2 seconds so the user can see it.
                elapsed_time = time.time() - start_time
                if elapsed_time < 2.0:
                    time.sleep(2.1 - elapsed_time)
                progress.kill()

    def _unlink_worker(self) -> None:
        """
        Removes all symlinks that match the current suffix.
        """
        start_time = time.time()
        progress: Optional[Progress] = None
        try:
            if self._config.show_progress:
                msg = self._rr.resolve_string("msg21")
                title = msg
                progress = Progress(start_msg=msg, title=title)
                progress.start()
            self._cp.unlink()
        except Exception as err:
            self._log.error(err, exc_info=True)
            return
        finally:
            if progress:
                # keep the progress window open for at least 2 seconds so the user can see it.
                elapsed_time = time.time() - start_time
                if elapsed_time < 2.0:
                    time.sleep(2.1 - elapsed_time)
                progress.kill()
                self._log.debug("Unlinking done.")
