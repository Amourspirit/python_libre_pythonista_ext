from __future__ import annotations
from typing import Any, List
import pandas as pd


class RuleBase:
    def __init__(self) -> None:
        pass

    def convert(self, value: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}()>"

    def get_all_date_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Gets all the date columns in a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to check.

        Returns:
            List[str]: A list of all the date columns in the DataFrame.
        """
        return [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
