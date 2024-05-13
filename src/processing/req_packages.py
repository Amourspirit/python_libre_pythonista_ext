from __future__ import annotations
from typing import Set

from .packages import Packages


class ReqPackages(Packages):
    """
    Required Packages Singleton Class.

    Windows does not have ``packaging`` installed by default.
    This class is used to ensure that ``packaging`` is available as it is required for this projects versioning classes.
    """

    # region Method Overrides
    def _get_package_names(self) -> Set[str]:
        """
        Gets the Package Names.

        The ``packaging`` package module is required in order to use the versioning classes in Windows LibreOffice Python.
        Package names added here are only available during the extension startup process, and is not available after LibreOffice is loaded.
        """
        return {"packaging"}

    def _get_package_files(self) -> Set[str]:
        return set()

    # endregion Method Overrides
