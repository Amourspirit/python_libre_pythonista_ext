from __future__ import annotations
from dataclasses import dataclass

from ooodev.utils.data_type.cell_obj import CellObj


@dataclass
class PySourceData:
    uri: str
    cell: CellObj
