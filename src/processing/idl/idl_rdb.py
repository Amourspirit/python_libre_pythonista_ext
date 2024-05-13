from __future__ import annotations
from pathlib import Path
import subprocess
from ...config import Config


class IdlRdb:
    """Class is responsible for compiling idl into rdb files."""

    def __init__(self) -> None:
        self._cfg = Config()
        self._idl_path = self._cfg.build_path / "sources"
        # get all the *.idl file from the idl directory
        if self._idl_path.exists():
            self._idl_files = list(self._idl_path.glob("*.idl"))
        else:
            self._idl_files = []
        self._rdb_dir = self._cfg.build_path
        self._validate()

    def _validate(self) -> None:
        """Validate the configuration."""
        if not self.has_files:
            return
        if not self._cfg.oo_types_uno:
            raise ValueError("oo_types_uno is empty")
        if not self._cfg.oo_types_office:
            raise ValueError("oo_types_office is empty")

    def _get_command(self, fnm: Path) -> str:
        # unoidl-write $OO_TYPES_UNO $OO_TYPES_OFFICE XFileName.idl XFileName.rdb
        out = self._rdb_dir / f"{fnm.stem}.rdb"
        return f"unoidl-write {self._cfg.oo_types_uno} {self._cfg.oo_types_office} {fnm} {out}"

    def compile(self) -> None:
        """Compile the idl files into rdb files."""
        if not self.has_files:
            return
        for idl_file in self._idl_files:
            cmd = self._get_command(idl_file)
            # run the command as a subprocess and wait for the subprocess to be done.
            subprocess.run(cmd, shell=True, check=True)

    # region Properties
    def has_files(self) -> bool:
        """Check if there are any idl files in the idl directory."""
        return bool(self._idl_files)

    # endregion Properties
