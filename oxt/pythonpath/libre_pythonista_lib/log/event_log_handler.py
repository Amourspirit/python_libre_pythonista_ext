from __future__ import annotations
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

import logging


class EventLogHandler(logging.Handler, EventsPartial):
    def __init__(self, *args, uid: str, **kwargs) -> None:  # noqa: ANN002, ANN003
        self._uid = uid
        logging.Handler.__init__(self, *args, **kwargs)
        EventsPartial.__init__(self)
        # Initialization code for your handler (e.g., open a file, establish a network connection)

    def emit(self, record: logging.LogRecord) -> None:
        # This method will be called for every log message
        # You can format the record as you wish using self.format(record)
        log_message = self.format(record)
        dd = DotDict(log_msg=log_message, record=record, log_level=self.level, uid=self._uid)
        eargs = EventArgs(self)
        eargs.event_data = dd
        self.trigger_event("log_emit", eargs)

        # Implement your custom handling logic here (e.g., write to a file, send over network)
