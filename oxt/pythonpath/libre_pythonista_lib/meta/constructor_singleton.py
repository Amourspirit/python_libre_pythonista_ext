from __future__ import annotations
from typing import Any


class ConstructorSingleton(type):
    """
    Singleton class that uses constructor arguments to determine if an instance should be created.

    Only keyword arguments are supported.
    Keyword arguments must be hashable.

    May need to add a code block to class in order to satisfy type checker when no args are passed.

    .. code-block:: python

        if TYPE_CHECKING:
            # just for singleton because there are no **kwargs by default.
            @overload
            def __new__(cls) -> MyClass: ...

            @overload
            def __new__(cls, **kwargs: Any) -> MyClass:

            def __new__(cls, **kwargs: Any) -> MyClass:
                pass

    """

    _instances = {}

    def __call__(cls, *args, **kwargs):  # noqa: ANN002, ANN003, ANN204
        # convert kwargs into a tuple of items
        if not kwargs:
            key = "default"
        else:
            t_kwargs = tuple(kwargs.items())
            key = hash((t_kwargs))
        if key not in cls._instances:
            if args:
                raise ValueError("ConstructorSingleton does not support positional arguments.")
            cls._instances[key] = super().__call__(**kwargs)
        return cls._instances[key]

    def delete_instance(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Deletes an instance from the _instances dictionary."""
        # Example usage
        # cache1 = LRUCache(capacity=10)
        # LRUCache.delete_instance(capacity=10)
        if not kwargs:
            key = "default"
        else:
            t_kwargs = tuple(kwargs.items())
            key = hash((t_kwargs))
        if key in cls._instances:
            del cls._instances[key]
