from __future__ import annotations
from typing import List
import pandas as pd


class PandasUtil:
    """Pandas utility class."""

    @staticmethod
    def has_headers(df: pd.DataFrame) -> bool:
        """Detects if a DataFrame has a header."""
        return not df.columns.is_unique or not all(isinstance(col, (int, float)) for col in df.columns)

    @staticmethod
    def has_index_names(df: pd.DataFrame) -> bool:
        """Detects if a DataFrame has index names."""
        return not pd.RangeIndex(start=0, stop=df.shape[0]).equals(df.index)

    @staticmethod
    def get_index_names(df: pd.DataFrame) -> list:
        """Returns the index names of a DataFrame."""
        return df.index.tolist()
