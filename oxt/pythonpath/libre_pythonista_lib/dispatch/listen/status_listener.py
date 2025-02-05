from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING

from com.sun.star.frame import ControlCommand
from com.sun.star.beans import NamedValue
from com.sun.star.frame import FeatureStateEvent

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.util import URL

# https://github.com/marklh9/ExtendingLibreOffice/blob/71a15e72bd9975c282b2d4e858ad933f44d0c3ee/src/ComplexToolbar/pythonpath/status_listener.py


def create_named_value(name: str, value: Any) -> NamedValue:  # noqa: ANN401
    v = NamedValue()
    v.Name = name
    v.Value = value
    return v


def create_control_command(command: str, arguments: Tuple[NamedValue]) -> ControlCommand:
    control_command = ControlCommand()
    control_command.Command = command
    control_command.Arguments = arguments
    return control_command


class FeatureEventWrapper:
    def __init__(self, url: URL, enabled: bool, requery: bool) -> None:
        event = FeatureStateEvent()
        event.FeatureURL = url
        event.IsEnabled = enabled
        event.Requery = requery
        self.event = event

    def set_command(self, command: str, name: str, value: Any) -> FeatureStateEvent:  # noqa: ANN401
        args = (create_named_value(name, value),)
        self.event.State = create_control_command(command, args)
        return self.event

    def set_command_with_args(self, command: str, **kwargs: str) -> FeatureStateEvent:
        arglist = []
        for name, value in kwargs.items():
            arglist.append(create_named_value(name, value))
        self.event.State = create_control_command(command, tuple(arglist))
        return self.event

    def set_state(self, state: Any) -> FeatureStateEvent:  # noqa: ANN401
        self.event.State = state
        return self.event


class StatusListenerWrapper:
    def __init__(self, listener: XStatusListener, url: URL) -> None:
        self.listener = listener
        self.url = url

    def send_command(self, command: str, name: str, value: Any) -> StatusListenerWrapper:  # noqa: ANN401
        event = FeatureEventWrapper(self.url, True, False)
        self.listener.statusChanged(event.set_command(command, name, value))
        return self

    def send_command_with_args(self, command: str, **kwargs: str) -> StatusListenerWrapper:
        event = FeatureEventWrapper(self.url, True, False)
        self.listener.statusChanged(event.set_command_with_args(command, **kwargs))
        return self

    def change_state(self, state: Any) -> StatusListenerWrapper:  # noqa: ANN401
        event = FeatureEventWrapper(self.url, True, False)
        self.listener.statusChanged(event.set_state(state))
        return self
