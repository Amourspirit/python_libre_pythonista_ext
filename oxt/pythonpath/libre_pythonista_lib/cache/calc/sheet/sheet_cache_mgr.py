from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING, Set, Dict


from ooodev.calc import CalcSheet
from ooodev.events.args.event_args import EventArgs
from ooodev.events.partial.events_partial import EventsPartial


if TYPE_CHECKING:
    from ooodev.utils.cache import MemCache
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache

_KEY = "libre_pythonista_lib.cache.calc.sheet.sheet_cache_mgr.SheetCacheMgr"

# see: cq.qry.qry_handler._handle_sheet_managed_cache()
# see cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet.QryLpCellsBySheet


class SheetCacheMgr(LogMixin, EventsPartial):
    """
    Manages caching for a specific sheet. Implements singleton pattern per sheet.

    Inherits from LogMixin for logging capabilities and EventsPartial for event handling.
    """

    def __new__(cls, sheet: CalcSheet) -> SheetCacheMgr:
        """
        Ensures only one instance exists per sheet by storing it in the sheet's cache.

        Args:
            sheet (CalcSheet): The sheet to manage caching for

        Returns:
            SheetCacheMgr: Either existing instance or newly created one
        """
        sheet_cache = get_sheet_cache(sheet)
        if _KEY in sheet_cache:
            return sheet_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False
        inst.sheet_cache = sheet_cache

        sheet_cache[_KEY] = inst
        return inst

    def __init__(self, sheet: CalcSheet) -> None:
        """
        Initializes the cache manager for a sheet. Only runs once per instance.

        Args:
            sheet (CalcSheet): The sheet to manage caching for
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        EventsPartial.__init__(self)
        self.sheet_cache: MemCache
        self._cache_keys: Dict[str, Set[str]] = {}
        self._sheet = sheet
        se = SharedEvent(sheet.calc_doc)
        se.add_event_observers(self.event_observer)
        self._fn_on_event = self._on_event
        self.log.debug("Init completed for sheet: %s", sheet.name)
        self._is_init = True

    def _on_event(self, src: Any, event: EventArgs) -> None:  # noqa: ANN401
        """
        Event handler that removes cached items when registered events occur.

        Args:
            src (Any): Event source
            event (EventArgs): Event arguments containing event details
        """
        self.log.debug("_on_event()")
        for key, event_names in self._cache_keys.items():
            for event_name in event_names:
                if event_name != event.event_name:
                    continue
                self.sheet_cache.remove(key)
                self.log.debug("Removed event %s for cache key: %s", event_name, key)

    def register_key(self, key: str, event_name: str) -> None:
        """
        Registers a cache key to be cleared when a specific event occurs.

        Args:
            key (str): Cache key to register
            event_name (str): Event name that triggers cache clearing
        """
        if key not in self._cache_keys:
            self._cache_keys[key] = set()
        self._cache_keys[key].add(event_name)
        self.unsubscribe_event(event_name, self._fn_on_event)
        self.subscribe_event(event_name, self._fn_on_event)
        self.log.debug("Registered key: %s", key)

    def unregister_key(self, key: str, event_name: str) -> None:
        """
        Removes registration of a cache key for a specific event.

        Args:
            key (str): Cache key to unregister
            event_name (str): Event name to unregister
        """
        if key not in self._cache_keys:
            return
        self.unsubscribe_event(event_name, self._fn_on_event)
        self.log.debug("Unregistered key: %s", key)
        self._cache_keys[key].remove(event_name)
        if not self._cache_keys[key]:
            del self._cache_keys[key]

    @property
    def sheet(self) -> CalcSheet:
        """
        Gets the sheet being managed.

        Returns:
            CalcSheet: The managed sheet
        """
        return self._sheet
