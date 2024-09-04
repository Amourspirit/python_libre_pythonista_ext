from __future__ import annotations
from datetime import datetime, timedelta
import pandas as pd
from ooodev.loader import Lo


class ConvertUtil:
    @staticmethod
    def pandas_timestamp_to_iso8601(timestamp: pd.Timestamp) -> str:
        """
        Convert a pandas Timestamp to an ISO 8601 string.

        Args:
            timestamp (pd.Timestamp): The pandas Timestamp to convert.

        Returns:
            str: The ISO 8601 string representation of the timestamp.
        """
        return timestamp.isoformat()

    @staticmethod
    def pandas_timedelta_to_iso8601(timedelta: pd.Timedelta) -> str:
        """
        Convert a pandas Timedelta to an ISO 8601 duration string.

        Args:
            timedelta (pd.Timedelta): The pandas Timedelta to convert.

        Returns:
            str: The ISO 8601 duration string representation of the timedelta.
        """
        total_seconds = int(timedelta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Constructing the ISO 8601 duration string
        duration = f"P{days}DT{hours}H{minutes}M{seconds}S"
        return duration

    @staticmethod
    def get_lo_epoch() -> datetime:
        """
        Get the epoch used by LibreOffice Calc.

        Returns:
            datetime: The epoch used by LibreOffice Calc.
        """
        nd = Lo.null_date  # contains timezone of utc
        return datetime(nd.year, nd.month, nd.day)

    @classmethod
    def lo_date_to_pandas_timestamp(cls, numeric_date: float) -> pd.Timestamp:
        """
        Convert a LibreOffice Calc numeric date to a Pandas Timestamp.

        Args:
            numeric_date (float): The numeric date to convert.

        Returns:
            pd.Timestamp: The Pandas Timestamp representation of the numeric date.
        """
        # LibreOffice Calc's epoch
        epoch = cls.get_lo_epoch() # must not contain tz
        # epoch = datetime(1899, 12, 30)
        # Convert numeric date to datetime
        date_time = epoch + timedelta(days=numeric_date)
        # Convert datetime to Pandas Timestamp
        pandas_timestamp = pd.Timestamp(date_time)
        return pandas_timestamp

    @classmethod
    def pandas_to_lo_date(cls, timestamp: pd.Timestamp | datetime) -> int:
        """
        Convert a Pandas Timestamp or datetime object to a LibreOffice Calc numeric date.

        Args:
            timestamp (pd.Timestamp | datetime): The Pandas Timestamp or datetime object to convert.

        Returns:
            int: The LibreOffice Calc numeric date representation of the timestamp.
        """
        # Base date for LibreOffice Calc
        epoch = cls.get_lo_epoch() # must not contain tz
        # epoch = datetime(1899, 12, 30)

        # Ensure the timestamp is a datetime object
        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()

        # Calculate the difference in days, including fractional part for time
        delta = timestamp - epoch
        libreoffice_number = delta.days + delta.seconds / 86400  # 86400 seconds in a day

        return round(libreoffice_number)
