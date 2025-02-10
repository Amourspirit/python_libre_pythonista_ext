from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, TYPE_CHECKING

from ooodev.utils.data_type.cell_obj import CellObj

# from .cell_code_storage import CellCodeStorage

if TYPE_CHECKING:
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

# _MOD_DIR = "librepythonista"


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


class PySource:
    def __init__(self, uri: str, cell: CellObj, src_provider: PySrcProvider | None = None) -> None:
        if getattr(self, "_is_init", False):
            return
        self._log = OxtLogger(log_name=self.__class__.__name__)
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
        self._src_code = None
        self._is_init = True

    def __lt__(self, other: Any) -> bool:  # noqa: ANN401
        # for sort
        if isinstance(other, PySource):
            addr1 = (self.sheet_idx, self.row, self.col)
            addr2 = (other.sheet_idx, other.row, other.col)
            return addr1 < addr2
        return NotImplemented

    def _get_source(self) -> str:
        """Reads the source code from the file. This method does not cache the source code"""
        self._log.debug("PySource._get_source() - Getting Source")
        if not self.exists():
            self._log.debug(
                f"PySource._get_source() - Source file does not exist: {self._uri}. Returning empty string."
            )
            return ""
        return self._src_provider.get_source()

    def _set_source(self, code: str) -> None:
        """Writes the source code to the file."""
        self._log.debug("PySource._set_source() - Setting Source")
        self._src_provider.ensure_src()
        self._src_provider.set_source(code)

    def del_source(self) -> None:
        """Deletes the source file."""
        self._log.debug("PySource.del_source() - Deleting Source")
        if self.exists():
            self._src_provider.del_source()
        else:
            self._log.debug("PySource.del_source() - Source folder does not exist.")

    def exists(self) -> bool:
        return self._src_provider.exists()

    @property
    def col(self) -> int:
        """Column zero based index."""
        return self._col

    @property
    def row(self) -> int:
        """Cell row zero based index."""
        return self._row

    @property
    def sheet_idx(self) -> int:
        """Sheet index zero based."""
        return self._sheet_idx

    @property
    def source_code(self) -> str:
        """Gets/Sets the source code from the file. This value is cached after the first call."""
        if self._src_code is None:
            self._src_code = self._get_source()
        return self._src_code

    @source_code.setter
    def source_code(self, code: str) -> None:
        self._set_source(code)
        self._src_code = code
