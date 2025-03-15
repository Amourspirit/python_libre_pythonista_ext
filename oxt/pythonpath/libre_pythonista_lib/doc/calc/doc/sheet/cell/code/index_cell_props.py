from __future__ import annotations
from typing import Set
from dataclasses import dataclass, field


@dataclass
class IndexCellProps:
    code_name: str
    props: Set[str]
    index: int = field(default=-1)

    def __hash__(self) -> int:
        return hash((self.index, self.props))
