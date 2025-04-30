from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import override as override
else:

    def override(func):  # noqa: ANN001, ANN201
        return func
