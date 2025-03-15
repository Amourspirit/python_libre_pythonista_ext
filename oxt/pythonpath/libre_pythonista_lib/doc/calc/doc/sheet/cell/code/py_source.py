from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.utils.helper.dot_dict import DotDict

# from .cell_code_storage import CellCodeStorage

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin


@dataclass
class UrlInfo:
    url: str
    protocol: str
    path: str
    runtime_id: str
    code_dir: str
    unique_id: str
    name: str
    ext: str

    @property
    def full_name(self) -> str:
        return f"{self.name}.{self.ext}"

    @staticmethod
    def from_url(url: str) -> UrlInfo:
        parts = url.split("/")
        protocol = parts[0]
        path = "/".join(parts[1:])
        unique_id = parts[-2]
        full_name = parts[-1]
        runtime_id = parts[1]
        code_dir = parts[2]
        name, ext = full_name.split(".")
        return UrlInfo(
            url=url,
            protocol=protocol,
            path=path,
            runtime_id=runtime_id,
            code_dir=code_dir,
            unique_id=unique_id,
            name=name,
            ext=ext,
        )


class PySrcProvider(ABC):
    def __init__(self, uri: str) -> None:
        self._uri = uri

    @abstractmethod
    def del_source(self) -> None:
        pass

    @abstractmethod
    def get_source(self) -> str:
        pass

    @abstractmethod
    def set_source(self, code: str) -> None:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    @abstractmethod
    def ensure_src(self) -> None:
        pass


class SfaProvider(PySrcProvider):
    def __init__(self, uri: str) -> None:
        super().__init__(uri)

        # uri is in format of:
        # vnd.sun.star.tdoc:/<uid>/<lp_code_dir>/<sheet_name>/<cell_name>.py

        from ooodev.io.sfa import Sfa

        self._sfa = Sfa()
        self._url_info = UrlInfo.from_url(uri)
        self._root_uri = f"vnd.sun.star.tdoc:/{self._url_info.runtime_id}/{self._url_info.code_dir}"

    def del_source(self) -> None:
        self._sfa.delete_file(self._uri)

    def get_source(self) -> str:
        return self._sfa.read_text_file(self._uri)

    def set_source(self, code: str) -> None:
        self._sfa.write_text_file(self._uri, code, "w")

    def exists(self) -> bool:
        return self._sfa.exists(self._uri)

    def ensure_src(self) -> None:
        if not self.exists():
            self._sfa.inst.create_folder(self._root_uri)


class PySource(LogMixin):
    """
    Manages Python source code stored in a LibreOffice document.

    This class handles reading, writing, and managing Python source code associated with a specific cell
    in a LibreOffice Calc document.

    Args:
        uri (str): URI to the source code file in the document
        cell (CellObj): Cell object that the source code is associated with
        src_provider (PySrcProvider | None): Provider for source code storage operations. Defaults to SfaProvider if None
    """

    def __init__(self, uri: str, cell: CellObj, src_provider: PySrcProvider | None = None) -> None:
        LogMixin.__init__(self)
        if src_provider is None:
            src_provider = SfaProvider(uri)
        self._src_provider = src_provider
        self._uri = uri
        self._cell_obj = cell
        # pth = Path(uri)
        # self._name = pth.stem
        self._row = cell.row - 1
        self._col = cell.col_obj.index
        self._sheet_idx = cell.sheet_idx
        self._uri_info = None
        self._dd_data = DotDict(data=None, py_src=self)

    def __lt__(self, other: object) -> bool:
        """
        Enables sorting PySource objects by sheet index, row, and column.

        Args:
            other (Any): Object to compare with

        Returns:
            bool: True if this object should be sorted before other
        """
        # for sort
        if isinstance(other, PySource):
            addr1 = (self.sheet_idx, self.row, self.col)
            addr2 = (other.sheet_idx, other.row, other.col)
            return addr1 < addr2
        return NotImplemented

    def __copy__(self) -> PySource:
        """Creates a shallow copy of this PySource instance."""
        return PySource(self._uri, self._cell_obj, self._src_provider)

    def _get_source(self) -> str:
        """
        Reads the source code from storage.

        Returns:
            str: The source code content or empty string if file doesn't exist
        """
        self.log.debug("PySource._get_source() - Getting Source")
        if not self.exists():
            self.log.debug(
                "PySource._get_source() - Source file does not exist: %s. Returning empty string.", self._uri
            )
            return ""
        return self._src_provider.get_source()

    def _set_source(self, code: str) -> None:
        """
        Writes source code to storage.

        Args:
            code (str): The source code to write
        """
        self.log.debug("PySource._set_source() - Setting Source")
        self._src_provider.ensure_src()
        self._src_provider.set_source(code)

    def del_source(self) -> None:
        """Deletes the source code file from storage."""
        self.log.debug("PySource.del_source() - Deleting Source")
        if self.exists():
            self._src_provider.del_source()
        else:
            self.log.debug("PySource.del_source() - Source folder does not exist.")

    def exists(self) -> bool:
        """
        Checks if the source code file exists.

        Returns:
            bool: True if file exists, False otherwise
        """
        return self._src_provider.exists()

    def copy(self) -> PySource:
        """Creates a copy of this PySource instance."""
        return self.__copy__()

    @property
    def col(self) -> int:
        """Zero-based column index of associated cell."""
        return self._col

    @property
    def row(self) -> int:
        """Zero-based row index of associated cell."""
        return self._row

    @property
    def sheet_idx(self) -> int:
        """Zero-based sheet index of associated cell."""
        return self._sheet_idx

    @property
    def source_code(self) -> str:
        """
        Gets or sets the source code content.

        Returns:
            str: The source code content
        """
        return self._get_source()

    @source_code.setter
    def source_code(self, code: str) -> None:
        self._set_source(code)

    @property
    def cell_obj(self) -> CellObj:
        """The cell object associated with this source code."""
        return self._cell_obj

    @property
    def uri(self) -> str:
        """URI of the source code file."""
        return self._uri

    @property
    def uri_info(self) -> UrlInfo:
        """
        Parsed information about the source URI.

        Returns:
            UrlInfo: Object containing parsed URI components
        """
        if self._uri_info is None:
            self._uri_info = UrlInfo.from_url(self._uri)
        return self._uri_info

    @property
    def dd_data(self) -> DotDict:
        return self._dd_data

    @dd_data.setter
    def dd_data(self, value: DotDict) -> None:
        self._dd_data = value
