from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
import re

from ooodev.utils.validation import check
from ooodev.utils.decorator import enforce

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.utils.custom_ext import override


# Note that from __future__ import annotations converts annotations to string.
# this means that @enforce.enforce_types will see string as type. This is fine in
# most cases. Especially for built in types.
@enforce.enforce_types
@dataclass(unsafe_hash=True)
class Addr:
    """Represents a address in the form of ``sheet_index=0&cell_addr=A1``"""

    value: str
    """str value."""

    def __post_init__(self) -> None:
        # match self.value to format of sheet_index=0&cell_addr=A1 where sheet_index is an int and cell_addr is a string.
        # use regex to match
        pattern = r"sheet_index=\d+&cell_addr=[A-Z]+\d+"

        check(
            bool(re.match(pattern, self.value)),
            f"{self}",
            f"Value of {self.value} is not a valid address. Value must be in format of sheet_index=0&cell_addr=A1",
        )

    @override
    def __eq__(self, other: object) -> bool:
        # for some reason BaseIntValue __eq__ is not picked up.
        # I suspect this is due to this class being a dataclass.
        try:
            s = str(other)  # type: ignore
            return s == self.value
        except Exception:
            return False

    @override
    def __str__(self) -> str:
        return self.value
