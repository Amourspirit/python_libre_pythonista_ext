from __future__ import annotations
from typing import Any, Dict, Tuple
import ssl
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


from ..meta.singleton import Singleton
from ..oxt_logger import OxtLogger
from ..config import Config


class Download(metaclass=Singleton):
    """Singleton class. Download file from url"""

    def __init__(self) -> None:
        self._logger = OxtLogger(log_name=__name__)

    def url_open(
        self,
        url: str,
        data: Any = None,
        headers: Dict[str, str] | None = None,
        verify: bool = True,
        get_json: bool = False,
    ) -> Tuple[Any, Dict[str, str], str]:
        """
        Download file from url

        Args:
            url (str): Url to download
            data (Any, optional): Data
            headers (Dict[str, str], optional): Headers
            verify (bool, optional): Verify ssl. Defaults to True.
            get_json (bool, optional): Get json. Defaults to False.

        Returns:
            Tuple[Any, Dict[str, str], str]: results
        """
        if headers is None:
            headers = {}
        if not self.is_internet:
            err = "No internet connection!"
            self._logger.error(err)
            return None, {}, err

        result = None
        err = ""
        req = Request(url)
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            # ~ debug(url)
            if verify:
                if data is not None and isinstance(data, str):
                    data = data.encode()
                response = urlopen(req, data=data)
            else:
                context = ssl._create_unverified_context()
                response = urlopen(req, context=context)
        except HTTPError as e:
            self._logger.error(e)
            err = str(e)
        except URLError as e:
            self._logger.error(e.reason)
            err = str(e.reason)
        else:
            headers = dict(response.info())
            result = response.read()
            if get_json:
                result = json.loads(result)

        return result, headers, err

    def save_binary(self, pth: Path | str, data: Any) -> bool:
        """
        Save binary data to file

        Args:
            pth (Path): Path to file
            data (Any): Binary data

        Returns:
            bool: True if success
        """
        if isinstance(pth, str):
            pth = Path(pth)
        return bool(pth.write_bytes(data))

    def check_internet_connection(self, url: str = "") -> bool:
        """
        Gets if there is an internet connection.

        If url is not provided then it will use the url from the config.
        If the config url is not provided then ``True`` will be returned.

        Args:
            url (str, optional): Test Url. Defaults to `Config().test_internet_url`.

        Returns:
            bool: ``True`` if there is an internet connection. ``False`` if no internet connection or if no url is provided.
        """
        try:
            if not url:
                url = Config().test_internet_url
            if not url:
                return False
            if url.startswith("https"):
                # do not verify sss
                context = ssl._create_unverified_context()
                _ = urlopen(url=url, timeout=5.0, context=context)
            else:
                _ = urlopen(url=url, timeout=5.0)
            return True
        except URLError:
            return False

    @property
    def is_internet(self) -> bool:
        """Gets if there is an internet connection."""
        try:
            return self._is_internet
        except AttributeError:
            self._is_internet = self.check_internet_connection()
            return self._is_internet
