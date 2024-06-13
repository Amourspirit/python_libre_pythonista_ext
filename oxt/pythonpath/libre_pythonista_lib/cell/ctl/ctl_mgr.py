from __future__ import annotations
from ooodev.events.args.event_args import EventArgs
from .float_ctl import FloatCtl
from .str_ctl import StrCtl


class CtlMgr:
    def __init__(self):
        pass

    def set_ctl(self, event: EventArgs):
        """
        Event handler for when a cell custom property is modified.

        Args:
            event (EventArgs): Event data for when a cell custom property is modified.

        Note:
            ``event.event_data`` is a DotDict with the following keys:
            - absolute_name: str
            - event_obj: ``com.sun.star.lang.EventObject``
            - code_name: str
            - trigger_name: str
            - remove_custom_property: bool
            - calc_cell: CalcCell
            - cell_cp_codename: Unique code name for cell custom property
        """
        trigger_name = event.event_data.trigger_name
        if trigger_name in ("cell_data_type_float", "cell_data_type_int"):
            ctl = FloatCtl(event)
            ctl.add_ctl()
        elif trigger_name == "cell_data_type_str":
            ctl = StrCtl(event)
            ctl.add_ctl()
