from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from ...py_packages.packages import Packages
from ....lo_util.target_path import TargetPath
from ....config import Config
from ....oxt_logger import OxtLogger


class BatchWriter(ABC):
    def __init__(self) -> None:
        self._packages = Packages()
        self._target_path = TargetPath()
        self._config = Config()
        self._log = OxtLogger(log_name=self.__class__.__name__)

    @abstractmethod
    def write_file(self) -> None:
        """
        Write the file.
        """
        raise NotImplementedError

    @abstractmethod
    def get_contents(self) -> str:
        """
        Get the contents of the batch file.

        Returns:
            str: Contents of the batch file
        """
        raise NotImplementedError

    @property
    def packages(self) -> Packages:
        return self._packages

    @property
    def target_path(self) -> TargetPath:
        return self._target_path

    @property
    def log(self) -> OxtLogger:
        return self._log

    @property
    def config(self) -> Config:
        return self._config

    @property
    @abstractmethod
    def script_file(self) -> Path:
        raise NotImplementedError
