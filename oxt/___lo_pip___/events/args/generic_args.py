from __future__ import annotations
from typing import Dict, Any


class GenericArgs:
    """Generic Args"""

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        self._args = args[:]
        self._kwargs = kwargs.copy()

    @property
    def args(self) -> tuple:
        """
        Gets args tuple.

        This is a copy of ``args`` passed into constructor.
        """
        return self._args

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Gets kwargs Dictionary

        This is a copy of ``kwargs`` passed into constructor
        """
        return self._kwargs
