from __future__ import annotations
from typing import Any, Tuple
import pandas as pd


class PandasUtil:
    """Pandas utility class."""

    @staticmethod
    def is_dataframe(data: Any) -> bool:
        """Determines if the data is a pandas DataFrame."""
        return isinstance(data, pd.DataFrame)

    @staticmethod
    def has_headers(df: pd.DataFrame) -> bool:
        """Detects if a DataFrame has a header."""
        return not df.columns.is_unique or not all(isinstance(col, (int, float)) for col in df.columns)

    @staticmethod
    def has_index_names(df: pd.DataFrame) -> bool:
        """
        Detects if a DataFrame has index names.

        Note:
            This method will return True if the DataFrame has index names.
            This will return True for Head and Tail DataFrames.
        """

        return not pd.RangeIndex(start=0, stop=df.shape[0]).equals(df.index)

    @staticmethod
    def get_index_names(df: pd.DataFrame) -> list:
        """Returns the index names of a DataFrame."""
        return df.index.tolist()

    @classmethod
    def pandas_to_array(cls, df: pd.DataFrame, header_opt: int = 0, index_opt: int = 0) -> Any:
        """
        Converts a pandas DataFrame into a 2D list.

        This method automatically detects if the DataFrame has headers and index names.

        Args:
            df (pd.DataFrame): The DataFrame to convert.
            header_opt (int): If ``0``, then headers are included if they exist.
                If ``1``, then header names are included.
                If ``2``, then header names are not included.
                Default is ``0``.
            index_opt(int): If ``0``, then index names are included if they exist.
                If ``1``, then index names are included.
                If ``2``, then index names are not included.
                Default is ``0``.

        Returns:
            Any: The 2D list.
        """
        headers = [[]]
        if header_opt == 1:
            has_headers = True
        elif header_opt == 2:
            has_headers = False
        else:
            has_headers = cls.has_headers(df)
        if has_headers:
            headers = [df.columns.tolist()]
        # Append the DataFrame values to the list
        list_values = df.values.tolist()
        if not list_values:
            return headers

        if index_opt == 1:
            has_index_names = True
        elif index_opt == 2:
            has_index_names = False
        else:
            has_index_names = cls.has_index_names(df)

        if has_index_names:
            index_names = cls.get_index_names(df)
            # insert an index name into each row
            for i, index_name in enumerate(index_names):
                list_values[i].insert(0, index_name)
            # insert an empty value into the start of the headers
            if has_headers:
                headers[0].insert(0, "")

        if has_headers:
            result = headers + list_values
        else:
            result = list_values
        return result

    @classmethod
    def get_df_rows_columns(cls, df: pd.DataFrame) -> Tuple[int, int]:
        """Returns the number of rows and columns in a DataFrame."""
        has_headers = cls.has_headers(df)
        has_index_names = cls.has_index_names(df)
        shape = df.shape
        shape_len = len(shape)
        lst = [0, 0]
        if shape_len == 0:
            return lst[0], lst[1]

        if shape_len == 1:
            lst[0] = shape[0]
        else:
            lst[0] = shape[0]
            lst[1] = shape[1]
        if has_headers:
            lst[0] += 1

        if has_index_names:
            lst[1] += 1
        return lst[0], lst[1]

    @classmethod
    def get_df_index_max_len(cls, df: pd.DataFrame) -> int:
        """
        Gets the maximum length, string length, of the index names in a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to check.

        Returns:
            int: The maximum length of the index names.
        """
        has_index_names = cls.has_index_names(df)
        if not has_index_names:
            rows, _ = cls.get_df_rows_columns(df)
            return len(str(rows))
        # find the index row name that is the longest and return is length
        index_names = cls.get_index_names(df)
        return max(len(str(name)) for name in index_names)
