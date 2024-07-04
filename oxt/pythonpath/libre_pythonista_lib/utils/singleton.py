"""
Singletons must be isolated to current document instance.
When a new document is created, the singleton must be reinitialized.
"""

from __future__ import annotations
from typing import Any


class SingletonMeta(type):
    """
    Singleton metaclass
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if not "single_key" in kwargs:
            key = cls._get_single_key()
        else:
            key = kwargs.pop("single_key")
        if not key:
            raise ValueError("Unable to get single_key")
        if key not in cls._instances:
            inst = super().__call__(*args, **kwargs)
            inst.singleton_key = key
            cls._instances[key] = inst
        return cls._instances[key]

    def _get_single_key(cls) -> Any:
        from ooodev.loader import Lo

        return f"{Lo.current_doc.runtime_uid}_uid_{cls.__name__}"

    def remove_instance(cls, key: Any) -> None:
        if key in cls._instances:
            del cls._instances[key]

    def remove_instance_by_uid(cls, uid: str) -> None:
        start_key = f"{uid}_uid_"
        rm_keys = [k for k in cls._instances.keys() if isinstance(k, str) and k.startswith(start_key)]
        for key in rm_keys:
            del cls._instances[key]

    def remove_this_instance(cls, inst: Any) -> None:
        key = getattr(inst, "singleton_key", None)
        if not key:
            return
        if key in cls._instances:
            del cls._instances[key]

    def has_singleton_instance(cls) -> bool:
        """
        Checks if a singleton instance exists by checking for its class name in the keys.

        This is specific to the current document instance.
        """
        key_inst = cls._get_single_key()
        for key in cls._instances.keys():
            if key == key_inst:
                return True
        return False
