from __future__ import annotations
import contextlib
from typing import Any, Tuple, List, TYPE_CHECKING
from datetime import datetime, timedelta
import pandas as pd

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.convert import array as convert_array
    from oxt.pythonpath.libre_pythonista_lib.convert import pandas as convert_pandas
    from oxt.pythonpath.libre_pythonista_lib.convert.array import rules as array_rules
    from oxt.pythonpath.libre_pythonista_lib.convert.pandas import pd_rules as pandas_rules
else:
    from libre_pythonista_lib.convert import array as convert_array
    from libre_pythonista_lib.convert import pandas as convert_pandas
    from libre_pythonista_lib.convert.array import rules as array_rules
    from libre_pythonista_lib.convert.pandas import pd_rules as pandas_rules


class PandasUtil:
    """Pandas utility class."""

    @staticmethod
    def is_dataframe(data: Any) -> bool:  # noqa: ANN401
        """Determines if the data is a pandas DataFrame."""
        return isinstance(data, pd.DataFrame)

    @staticmethod
    def has_headers(df: pd.DataFrame) -> bool:
        """Detects if a DataFrame has a header."""
        return not df.columns.is_unique or not all(isinstance(col, (int, float)) for col in df.columns)

    @classmethod
    def has_index_names(cls, df: pd.DataFrame) -> bool:
        """
        Detects if a DataFrame has index names.

        Note:
            This method will return True if the DataFrame has index names.
            This will return True for Head and Tail DataFrames.
        """

        # return not pd.RangeIndex(start=0, stop=df.shape[0]).equals(df.index)
        result = False
        with contextlib.suppress(AttributeError):
            is_index = (
                (isinstance(df.index, pd.RangeIndex) or (df.index.dtype == "int64"))
                and df.index.name is None
                and df.index.names == [None]
            )
            result = not is_index
        return result

    @staticmethod
    def has_default_index(df: pd.DataFrame) -> bool:
        """
        Checks if the DataFrame has default numerical index values (pd.RangeIndex)
        and not named indexes.

        Returns:
            bool: True if the DataFrame has a default numerical index, False otherwise.
        """
        # https://thispointer.com/how-to-get-the-index-column-name-in-pandas/
        return isinstance(df.index, pd.RangeIndex) and df.index.name is None and df.index.names == [None]

    @staticmethod
    def get_index_names(df: pd.DataFrame) -> list:
        """Returns the index names of a DataFrame."""
        return df.index.tolist()

    @classmethod
    def pandas_to_array(
        cls, df: pd.DataFrame, *, header_opt: int = 0, index_opt: int = 0, convert: bool = True
    ) -> Any:  # noqa: ANN401
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
            convert (bool, optional): If True, converts dates to LibreOffice Calc numeric dates; Otherwise, converts dates to strings. Default is True.

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
        if convert:
            converter = convert_pandas.PandasDfConverter()
            converter.add_rule(pandas_rules.RulePdToLoDate)
            # converter.add_rule(pandas_rules.RulePdToIsoDate)
            list_values = converter.apply_rules(df).values.tolist()
        else:
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

        result = headers + list_values if has_headers else list_values
        return result

    @staticmethod
    def is_pandas_date_column(df: pd.DataFrame, column_name: str) -> bool:
        """
        Checks if the specified column in a DataFrame is of date type.

        Args:
            df (pd.DataFrame): The DataFrame to check.
            column_name (str): The name of the column to check.

        Raises:
            ValueError: If the column does not exist in the DataFrame.

        Returns:
            bool: True if the column is of date type, False otherwise.
        """
        # Check if the column exists in the DataFrame
        if column_name in df.columns:
            # Check if the column's dtype is 'datetime64[ns]'
            return pd.api.types.is_datetime64_any_dtype(df[column_name])
        else:
            raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    @staticmethod
    def get_all_date_columns(df: pd.DataFrame) -> List[str]:
        """
        Gets all the date columns in a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to check.

        Returns:
            List[str]: A list of all the date columns in the DataFrame.
        """
        return [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]

    @staticmethod
    def is_date_series(series: pd.Series) -> bool:
        """
        Checks if the Pandas Series is of date type.

        Args:
            series (pd.Series): The Series to check.

        Returns:
            bool: True if the Series is of date type, False otherwise.
        """
        # it's important to note that a Series represents a single column or row of data in Pandas, not multiple columns.
        return pd.api.types.is_datetime64_any_dtype(series)

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

    @classmethod
    def convert_dict_keys_to_lo_date(cls, data: dict) -> dict:
        """
        Converts the keys of a dictionary to LibreOffice Dates if the key is a Pandas Date.

        Args:
            data (dict): The dictionary to convert.

        Returns:
            dict: The dictionary with Pandas date keys.
        """
        result = {}
        for key, value in data.items():
            if isinstance(key, pd.Timestamp):
                result[cls.pandas_to_lo_date(key)] = value
            else:
                result[key] = value

        return result

    @staticmethod
    def lo_date_to_pandas(numeric_date) -> pd.Timestamp:
        # LibreOffice Calc's epoch
        epoch = datetime(1899, 12, 30)
        # Convert numeric date to datetime
        date_time = epoch + timedelta(days=numeric_date)
        # Convert datetime to Pandas Timestamp
        pandas_timestamp = pd.Timestamp(date_time)
        return pandas_timestamp

    @staticmethod
    def pandas_to_lo_date(timestamp: pd.Timestamp | datetime) -> int:
        # Base date for LibreOffice Calc
        base_date = datetime(1899, 12, 30)

        # Ensure the timestamp is a datetime object
        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()

        # Calculate the difference in days, including fractional part for time
        delta = timestamp - base_date
        libreoffice_number = delta.days + delta.seconds / 86400  # 86400 seconds in a day

        return round(libreoffice_number)

    @staticmethod
    def pandas_series_to_lo_calc(series: pd.Series) -> pd.Series:
        """
        Converts a Pandas Series of Timestamps to LibreOffice Calc date values.

        Args:
            series (pd.Series): Series containing pd.Timestamp objects.

        Returns:
            pd.Series: Series containing LibreOffice Calc date values.
        """
        # Define the base date for LibreOffice Calc
        base_date = datetime(1899, 12, 30)

        # Convert each Timestamp to the number of days since the base date
        libreoffice_values = series.apply(
            lambda x: (x - pd.Timestamp(base_date)).days + (x - pd.Timestamp(base_date)).seconds / 86400
        )

        return libreoffice_values

    @classmethod
    def convert_float64_to_dates(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Converts date columns to Pandas Timestamp."""
        for col in df.columns:
            if df[col].dtype == "float64":
                df[col] = df[col].apply(cls.lo_date_to_pandas)
        return df

    @classmethod
    def convert_lo_to_pandas_date_columns(cls, df: pd.DataFrame, *columns: str | int) -> pd.DataFrame:
        """
        Converts date columns to Pandas Timestamp.

        Columns are only converted if they exist in the DataFrame; Otherwise, they are ignored.

        Note:
            Does not make a copy of the DataFrame.
        """
        has_headers = cls.has_headers(df)
        # if there are no header then accessing cols via df[int] is valid
        # if there are headers then the columns are accessed via df[str]
        for col in columns:
            if isinstance(col, int):
                col_name = str(df.columns[col]) if has_headers else col
            # df.iloc[:, col] = df.iloc[:, col].apply(cls.lo_date_to_pandas)
            else:
                if not has_headers:
                    raise ValueError("Column name must be a string if DataFrame has no headers.")
                col_name = col
            if col_name in df.columns and not cls.pandas_is_date_col(df, col_name):
                df[col_name] = df[col_name].apply(cls.lo_date_to_pandas)
        return df

    @classmethod
    def convert_pandas_lo_date_columns(cls, df: pd.DataFrame, *columns: str | int) -> pd.DataFrame:
        """
        Converts date columns to Pandas Timestamp.

        Note:
            Does not make a copy of the DataFrame.

            Only applies to column that are not already date columns.
        """
        has_headers = cls.has_headers(df)
        # if there are no header then accessing cols via df[int] is valid
        # if there are headers then the columns are accessed via df[str]
        for col in columns:
            if isinstance(col, int):
                col_name = str(df.columns[col]) if has_headers else col
            # df.iloc[:, col] = df.iloc[:, col].apply(cls.pandas_to_lo_date)
            else:
                if not has_headers:
                    raise ValueError("Column name must be a string if DataFrame has no headers.")
                col_name = col
            if cls.pandas_is_date_col(df, col_name):
                df[col_name] = df[col_name].apply(cls.pandas_to_lo_date)
            # df[col] = df[col].apply(cls.pandas_to_lo_date)
        return df

    @classmethod
    def get_lo_converted_df(cls, df: pd.DataFrame, *columns: str) -> pd.DataFrame:
        """
        Converts LibreOffice Calc dates to Pandas Timestamp.

        If no conversion are need then the origin DataFrame is returned; Otherwise, a new DataFrame is returned.

        Note:
            If there are changes a copy is returned; Otherwise, the original DataFrame is returned.
        """
        # Most likely should build a rules engine for this.
        # instead of *columns this should be a list of objects.
        # an object will contain the column name and the type of conversion.
        if not columns:
            return df
        df_cpy = df.copy()
        cls.convert_lo_to_pandas_date_columns(df_cpy, *columns)
        return df_cpy

    @classmethod
    def get_pandas_converted_df(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts Pandas Calc dates to LibreOffice Timestamp.

        If no conversion are need then the origin DataFrame is returned; Otherwise, a new DataFrame is returned.

        Note:
            If there are changes a copy is returned; Otherwise, the original DataFrame is returned.
        """
        if cls.is_describe_output(df):
            return cls.get_pandas_converted_df_describe(df)
        # Most likely should build a rules engine for this.
        date_cols = cls.get_all_date_columns(df)
        if not date_cols:
            return df
        df_cpy = df.copy()
        cls.convert_lo_to_pandas_date_columns(df_cpy, *date_cols)
        return df_cpy

    @staticmethod
    def is_describe_output(df: pd.DataFrame) -> bool:
        """
        Attempts to determine if the DataFrame is likely the result of a df.describe() call.

        Args:
            df (pd.DataFrame): The DataFrame to check.

        Returns:
            bool: True if the DataFrame is likely the result of a describe() call, False otherwise.
        """
        # The pandas describe() method itself is not language-dependent in terms of its implementation
        # or the row names it generates.
        # The method produces summary statistics with fixed row names such as "count",
        # "mean", "std", "min", "25%", "50%", "75%", and "max", regardless of the
        # system's locale or the user's language settings.
        # These row names are hardcoded into the pandas source code and do not change
        # based on the system's language settings. Therefore, the output of describe()
        # in terms of these row names will be the same across different human languages.
        expected_rows = {"count", "mean", "std", "min", "25%", "50%", "75%", "max"}
        return set(df.index).issuperset(expected_rows)

    @classmethod
    def get_pandas_converted_df_describe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts LibreOffice Calc dates to Pandas Timestamp for a DataFrame that is likely the result of a describe() call.

        If no conversion are need then the origin DataFrame is returned; Otherwise, a new DataFrame is returned.

        Note:
            If there are changes a copy is returned; Otherwise, the original DataFrame is returned.
        """
        if not cls.is_describe_output(df):
            return df
        return cls.convert_pandas_df_describe_date_to_str(df)

    @staticmethod
    def timedelta_to_iso8601(timedelta: pd.Timedelta) -> str:
        total_seconds = int(timedelta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Constructing the ISO 8601 duration string
        duration = f"P{days}DT{hours}H{minutes}M{seconds}S"
        return duration

    @staticmethod
    def timestamp_to_iso8601(timestamp: pd.Timestamp) -> str:
        return timestamp.isoformat()

    @classmethod
    def convert_pandas_df_describe_date_to_str(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts date columns to strings for a DataFrame that is likely the result of a describe() call.

        Args:
            df (pd.DataFrame): The DataFrame to convert.

        Returns:
            pd.DataFrame: The DataFrame with date columns converted to strings.
        """
        describe_df = df.copy()
        for col in describe_df.select_dtypes(include=["datetime64[ns]"]).columns:
            describe_df[col] = describe_df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

        for col in describe_df.select_dtypes(include=["timedelta64[ns]"]).columns:
            df[col] = df[col].apply(cls.timedelta_to_iso8601)

        for col in describe_df.select_dtypes(include=[pd.Timestamp]).columns:
            describe_df[col] = describe_df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")
        return describe_df

    @classmethod
    def convert_array_to_lo(cls, data: list, date_str: bool = True) -> None:
        """
        Converts an array of Pandas Values to LibreOffice Calc Values.

        Args:
            data (list): The 2d list to convert.
            date_str (bool): If True, converts dates to string; Otherwise, converts dates to LibreOffice Calc numeric dates.

        Returns:
            list: Converted copy.

        Note:
            This is best for small arrays such as those from a ``DataFrame.describe()`` method or a card view.
        """
        arr = convert_array.ArrayRules()
        if date_str:
            arr.add_rule(array_rules.RulePdTimeStampIso)
        else:
            arr.add_rule(array_rules.RulePdTimeCalcNumDate)
        arr.add_rule(array_rules.RuleNone)
        arr.add_rule(array_rules.RuleNotKnown)

        for row in data:
            for i, cell in enumerate(row):
                rule = arr.get_matched_rule(cell)
                if rule:
                    row[i] = rule.convert(cell)
        return None

    @classmethod
    def pandas_is_date_col(cls, df: pd.DataFrame, col: str | int) -> bool:
        """
        Gets if a column is a date column.

        Args:
            df (DataFrame): The DataFrame to check.
            col (str | int): The column name or zero-based index to check.
        """
        # Test show that this work even if the df has no headers.
        if isinstance(col, str):
            return pd.api.types.is_datetime64_any_dtype(df[col])
        else:
            return pd.api.types.is_datetime64_any_dtype(df.iloc[:, col])
