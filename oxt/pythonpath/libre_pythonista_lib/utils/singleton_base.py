"""
Singletons must be isolated to current document instance.
When a new document is created, the singleton must be reinitialized.
"""

from __future__ import annotations
from typing import Any, cast
from ooodev.loader import Lo
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ..ex.exceptions import SingletonKeyError


class SingletonBase(object):
    """
    Singleton metaclass
    """

    _instances = {}

    def __new__(cls, *args, **kwargs) -> Any:  # noqa: ANN002, ANN003, ANN401
        key = cls._get_single_key() if "single_key" not in kwargs else kwargs.pop("single_key")
        if not key:
            raise ValueError("Unable to get single_key")
        if key not in cls._instances:
            cls.singleton_doc = Lo.current_doc
            inst = cast(Any, super().__new__(cls))
            inst.singleton_doc = Lo.current_doc
            inst.singleton_key = key
            inst.runtime_uid = inst.singleton_doc.runtime_uid  # type: ignore # key.split("_", maxsplit=1)[0]
            cls._instances[key] = inst
        return cls._instances[key]

    @classmethod
    def _get_single_key(cls) -> str:
        eargs = EventArgs(cls)
        eargs.event_data = DotDict(class_name=cls.__name__, key="")
        LoEvents().trigger("LibrePythonistaSingletonGetKey", eargs)
        if eargs.event_data.key:
            return eargs.event_data.key
        try:
            return f"{Lo.current_doc.runtime_uid}_uid_{cls.__name__}"  # type: ignore
        except Exception as e:
            raise SingletonKeyError(f"Error getting single key for class name: {cls.__name__}") from e

    @classmethod
    def remove_instance(cls, key: object) -> None:
        if key in cls._instances:
            del cls._instances[key]

    @classmethod
    def remove_instance_by_uid(cls, uid: str) -> None:
        start_key = f"{uid}_uid_"
        rm_keys = [k for k in cls._instances if isinstance(k, str) and k.startswith(start_key)]
        for key in rm_keys:
            del cls._instances[key]

    @classmethod
    def remove_this_instance(cls, inst: object) -> None:
        key = getattr(inst, "singleton_key", None)
        if not key:
            return
        if key in cls._instances:
            del cls._instances[key]

    @classmethod
    def has_singleton_instance(cls) -> bool:
        """
        Checks if a singleton instance exists by checking for its class name in the keys.

        This is specific to the current document instance.
        """
        key_inst = cls._get_single_key()
        return any(key == key_inst for key in cls._instances)
