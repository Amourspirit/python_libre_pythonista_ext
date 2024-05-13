# coding: utf-8
"""General Utilities"""

from __future__ import annotations
import contextlib
import re
from typing import Iterator, NamedTuple, Any, Sequence, TypeVar
from inspect import isclass

# match:
#   Any uppercase character that is not at the start of a line
#   Any Number that is preceded by a Upper or Lower case character
_REG_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])|(?<=[A-zA-Z])(?=[0-9])")  # re.compile(r"(?<!^)(?=[A-Z])")
_REG_LETTER_AFTER_NUMBER = re.compile(r"(?<=\d)(?=[a-zA-Z])")

NULL_OBJ = object()
"""Null Object uses with None is not an option"""

TNullObj = TypeVar("TNullObj", bound=object)


class ArgsHelper:
    "Args Helper"

    class NameValue(NamedTuple):
        "Name Value pair"
        name: str
        """Name component"""
        value: Any
        """Value component"""


class Util:
    @classmethod
    def is_iterable(cls, arg: Any, excluded_types: Sequence[type] | None = None) -> bool:
        """
        Gets if ``arg`` is iterable.

        Args:
            arg (object): object to test
            excluded_types (Iterable[type], optional): Iterable of type to exclude.
                If ``arg`` matches any type in ``excluded_types`` then ``False`` will be returned.
                Default ``(str,)``

        Returns:
            bool: ``True`` if ``arg`` is an iterable object and not of a type in ``excluded_types``;
            Otherwise, ``False``.

        Note:
            if ``arg`` is of type str then return result is ``False``.

        .. collapse:: Example

            .. code-block:: python

                # non-string iterables
                assert is_iterable(arg=("f", "f"))       # tuple
                assert is_iterable(arg=["f", "f"])       # list
                assert is_iterable(arg=iter("ff"))       # iterator
                assert is_iterable(arg=range(44))        # generator
                assert is_iterable(arg=b"ff")            # bytes (Python 2 calls this a string)

                # strings or non-iterables
                assert not is_iterable(arg=u"ff")        # string
                assert not is_iterable(arg=44)           # integer
                assert not is_iterable(arg=is_iterable)  # function

                # excluded_types, optionally exclude types
                from enum import Enum, auto

                class Color(Enum):
                    RED = auto()
                    GREEN = auto()
                    BLUE = auto()

                assert is_iterable(arg=Color)             # Enum
                assert not is_iterable(arg=Color, excluded_types=(Enum, str)) # Enum
        """
        # if isinstance(arg, str):
        #     return False
        if excluded_types is None:
            excluded_types = (str,)
        result = False
        try:
            result = isinstance(iter(arg), Iterator)
        except Exception:
            result = False
        if result and cls._is_iterable_excluded(arg, excluded_types=excluded_types):
            result = False
        return result

    @staticmethod
    def _is_iterable_excluded(arg: object, excluded_types: Sequence) -> bool:
        try:
            isinstance(iter(excluded_types), Iterator)
        except Exception:
            return False

        if len(excluded_types) == 0:
            return False

        def _is_instance(obj: object) -> bool:
            # when obj is instance then isinstance(obj, obj) raises TypeError
            # when obj is not instance then isinstance(obj, obj) return False
            with contextlib.suppress(TypeError):
                if not isinstance(obj, obj):  # type: ignore
                    return False
            return True

        ex_types = excluded_types if isinstance(excluded_types, tuple) else tuple(excluded_types)
        arg_instance = _is_instance(arg)
        if arg_instance is True:
            return isinstance(arg, ex_types)
        return True if isclass(arg) and issubclass(arg, ex_types) else arg in ex_types

    @staticmethod
    def to_camel_case(s: str) -> str:
        """
        Converts string to ``CamelCase``

        Args:
            s (str): string to convert such as ``snake_case_word`` or ``pascalCaseWord``

        Returns:
            str: string converted to ``CamelCaseWord``
        """
        s = s.strip()
        if not s:
            return ""
        result = s
        if "_" in result:
            return "".join(word.title() for word in result.split("_"))
        return result[:1].upper() + result[1:]

    @classmethod
    def to_pascal_case(cls, s: str) -> str:
        """
        Converts string to ``pascalCase``

        Args:
            s (str): string to convert such as ``snake_case_word`` or  ``CamelCaseWord``

        Returns:
            str: string converted to ``pascalCaseWord``
        """
        result = cls.to_camel_case(s)
        if result:
            result = result[:1].lower() + result[1:]
        return result

    @staticmethod
    def to_snake_case(s: str) -> str:
        """
        Convert string to ``snake_case``

        Args:
            s (str): string to convert such as ``pascalCaseWord`` or  ``CamelCaseWord``

        Returns:
            str: string converted to ``snake_case_word``
        """
        s = s.strip()
        if not s:
            return ""
        result = _REG_TO_SNAKE.sub("_", s)
        result = _REG_LETTER_AFTER_NUMBER.sub("_", result)
        return result.lower()

    @classmethod
    def to_snake_case_upper(cls, s: str) -> str:
        """
        Convert string to ``SNAKE_CASE``

        Args:
            s (str): string to convert such as ``snake_case_word`` or ``pascalCaseWord`` or  ``CamelCaseWord``

        Returns:
            str: string converted to ``SNAKE_CASE_WORD``
        """
        result = cls.to_snake_case(s)
        return result.upper() if s else ""

    @staticmethod
    def to_single_space(s: str, strip=True) -> str:
        """
        Gets a string with multiple spaces converted to single spaces

        Args:
            s (str): String
            strip (bool, optional): If ``True`` then whitespace is stripped from start and end or string. Default ``True``.

        Returns:
            str: String with extra spaces removed.

        Example:
            .. code-block:: python

                >>> s = ' The     quick brown    fox'
                >>> print(Util.to_single_space(s))
                'The quick brown fox'
        """
        if not s:
            return ""
        result = re.sub(" +", " ", s)
        return result.strip() if strip else result

    @staticmethod
    def _atoi(text):
        return int(text) if text.isdigit() else text

    @staticmethod
    def natural_key_sorter(text: str) -> list:
        """
        Sort Key Sorts in human order.

        # Example:

        .. code-block:: python

            a_list.sort(key=Util.natural_key_sorter)
        """
        # a_list.sort(key=natural_keys) sorts in human order
        # http://nedbatchelder.com/blog/200712/human_sorting.html
        # (See Toothy's implementation in the comments)
        # https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
        return [Util._atoi(c) for c in re.split(r"(\d+)", text)]
