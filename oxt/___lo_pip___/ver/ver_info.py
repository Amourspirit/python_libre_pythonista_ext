from __future__ import annotations
from importlib.metadata import version, PackageNotFoundError


def get_package_version(package_name: str) -> str:
    """
    Get the version of a package.

    Args:
        package_name (str): The name of the package such as ``verr``

    Returns:
        str: The version of the package or an empty string if the package is not installed.
    """
    try:
        return version(package_name)
    except PackageNotFoundError:
        return ""
