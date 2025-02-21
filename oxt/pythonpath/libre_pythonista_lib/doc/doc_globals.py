from __future__ import annotations
from typing import Any, TYPE_CHECKING
import os
from enum import Enum
import uno
from ooodev.loader import Lo
from ooodev.utils.cache import LRUCache
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.events.partial.events_partial import EventsPartial

from ooodev.meta.class_property_readonly import ClassPropertyReadonly

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import DOC_GBL_DEL_INSTANCE
    from oxt.pythonpath.libre_pythonista_lib.cache.mem_cache import MemCache
else:
    from libre_pythonista_lib.const.event_const import DOC_GBL_DEL_INSTANCE
    from libre_pythonista_lib.cache.mem_cache import MemCache


class _MetaGlobals(type):
    """
    Singleton class that uses constructor arguments to determine if an instance should be created.

    Only keyword arguments are supported.
    Keyword arguments must be hashable.
    """

    _instances = {}
    RUNTIME_IDS = []

    def __call__(cls, *args, runtime_uid: str, **kwargs):  # noqa: ANN002, ANN003, ANN204
        # convert kwargs into a tuple of items

        kwargs["runtime_uid"] = runtime_uid
        t_kwargs = tuple(kwargs.items())
        i = hash((t_kwargs))
        key = f"{cls.__name__}_{i}"
        if key not in cls._instances:
            cls.RUNTIME_IDS.append(runtime_uid)
            if args:
                raise ValueError("_MetaGlobals does not support positional arguments.")
            cls._instances[key] = super().__call__(**kwargs)
        return cls._instances[key]

    def delete_instance(cls, runtime_uid: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Deletes an instance from the _instances dictionary."""
        # Example usage
        # gbl = DocGlobals(runtime_uid="1")
        # DocGlobals.delete_instance(runtime_uid="1")
        kwargs["runtime_uid"] = runtime_uid
        t_kwargs = tuple(kwargs.items())
        i = hash((t_kwargs))
        key = f"{cls.__name__}_{i}"
        if key in cls._instances:
            inst = cls._instances[key]
            inst.on_delete_instance()
            inst = None
            if runtime_uid in cls.RUNTIME_IDS:
                cls.RUNTIME_IDS.remove(runtime_uid)
            del cls._instances[key]


class DocGlobals(EventsPartial, metaclass=_MetaGlobals):
    """
    Global variables for a LibreOffice document.

    This class is a singleton and is created for each LibreOffice document.
    """

    _IS_PYTEST_RUNNING = "PYTEST_CURRENT_TEST" in os.environ

    class CacheType(Enum):
        CALC_SHEET = "libre_pythonista_lib_cache_calc_sheet_key"
        CALC_DOC = "libre_pythonista_lib_cache_calc_doc_key"

        def __str__(self) -> str:
            return self.value

    def __init__(self, *, runtime_uid: str) -> None:
        EventsPartial.__init__(self)
        self._runtime_uid = runtime_uid
        self._lru_cache = LRUCache(capacity=5000)
        self._mem_cache = MemCache()

    def on_delete_instance(self) -> None:
        """
        This method is called when the instance is deleted.
        """
        args = EventArgs(self)
        args.event_data = DotDict(runtime_uid=self._runtime_uid)
        self.trigger_event(DOC_GBL_DEL_INSTANCE, args)

    def _get_mem_cache_key(self, cache_type: CacheType, **kwargs: Any) -> str:  # noqa: ANN401
        t_kwargs = tuple(kwargs.items())
        cache_type_key = str(cache_type)
        i = hash((t_kwargs))
        return f"{cache_type_key}_{i}"

    def get_mem_cache(self, cache_type: CacheType, **kwargs: Any) -> MemCache:  # noqa: ANN401
        """
        Get a specific cache instance.

        Args:
            cache_type (CacheType): The cache type.
            kwargs (Any): Additional keyword arguments that are uses when creating cache key.
                Kwarg keys must be hashable.

        Returns:
            MemCache: The cache instance.
        """

        key = self._get_mem_cache_key(cache_type, **kwargs)
        if key not in self.mem_cache:
            self.mem_cache[key] = MemCache()
        return self.mem_cache[key]

    def remove_mem_cache(self, cache_type: CacheType, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Remove a specific cache instance.

        Args:
            cache_type (CacheType): The cache type.
            kwargs (Any): Additional keyword arguments that are uses when creating cache key.
                Kwarg keys must be hashable.
        """
        key = self._get_mem_cache_key(cache_type, **kwargs)
        if key in self.mem_cache:
            del self.mem_cache[key]

    # region Properties

    @property
    def lru_cache(self) -> LRUCache:
        """
        Least Recently Used (LRU) Cache

        This cache is unique to each LibreOffice document.

        Returns:
            LRUCache: The LRU cache instance.
        """
        return self._lru_cache

    @property
    def mem_cache(self) -> MemCache:
        """
        Memory Cache

        This cache is unique to each LibreOffice document.

        Returns:
            MemCache: The Memory cache instance.
        """
        return self._mem_cache

    @property
    def runtime_uid(self) -> str:
        """The runtime unique id of the LibreOffice document."""
        return self._runtime_uid

    # endregion Properties

    # region Static Methods
    @ClassPropertyReadonly
    @classmethod
    def is_pytest_running(cls) -> bool:  # noqa: N805
        """Check if the code is running under pytest."""
        return cls._IS_PYTEST_RUNNING

    @staticmethod
    def get_current() -> DocGlobals:
        """
        Get the current DocGlobals instance.
        The instance is derived from the current LibreOffice document.

        Raises:
            ValueError: If there is no current document.

        Returns:
            DocGlobals: The current DocGlobals instance.
        """
        doc_component = Lo.current_lo.desktop.get_current_component()
        uid = None

        # If a document has been closed and focus has not been set to another document
        # then the current document will be None.
        # In this case, we can use the last runtime id if it exists.
        # When a document is closed it uid is removed from the RUNTIME_IDS list.
        # This is done in the Cleanup Job.

        if doc_component is None and Lo.is_macro_mode:
            ctx = uno.getComponentContext()
            service_mgr = ctx.getServiceManager()  # type: ignore
            desktop = service_mgr.DefaultContext.getByName("/singletons/com.sun.star.frame.theDesktop")
            doc_component = desktop.getCurrentComponent()

        if doc_component is not None:
            uid = doc_component.RuntimeUID  # type: ignore
            # print(f"DocGlobals.get_current() - uid: {uid}")
        else:
            if DocGlobals.RUNTIME_IDS:
                uid = DocGlobals.RUNTIME_IDS[-1]

        if uid is None:
            raise ValueError("No current document.")
        # print(f"DocGlobals.get_current() - uid: {uid}")
        return DocGlobals(runtime_uid=uid)

    @classmethod
    def get_current_mem_cache(cls) -> MemCache:
        """
        Get the current DocGlobals MemCache instance.

        Raises:
            ValueError: If there is no current document.

        Returns:
            MemCache: The current MemCache instance.
        """
        current = cls.get_current()
        return current.mem_cache

    # endregion Static Methods
