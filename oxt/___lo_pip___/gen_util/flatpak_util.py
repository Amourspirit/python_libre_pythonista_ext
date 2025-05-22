from __future__ import annotations
from typing import TYPE_CHECKING, Union
import subprocess

if TYPE_CHECKING:
    from ..oxt_logger import OxtLogger


def is_flatpak_app_installed(app_name: str, log: Union[OxtLogger, None] = None) -> bool:
    """
    Check if a Flatpak application is installed on the system.

    Args:
        app_name (str): The name of the Flatpak application to check.
        log (OxtLogger, None, optional): An optional logger to use for logging errors. Defaults to None.

    Returns:
        bool: True if the application is installed, False otherwise.

    Note:
        This method is intended to be run in a Flatpak environment. If it is run outside of a Flatpak environment, it will return False.

    Example:
        .. code-block:: python

            app_name = "io.github.amourspirit.LibrePythonista_PyEditor"
            if is_flatpak_app_installed(app_name):
                print(f"{app_name} is installed.")
            else:
                print(f"{app_name} is not installed.")
    """

    try:
        # Run the flatpak list command to get the list of installed apps
        result = subprocess.run(
            ["/usr/bin/flatpak-spawn", "--host", "flatpak", "list"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Check if the app_name is in the list of installed apps
        installed_apps = result.stdout.splitlines()
        for app in installed_apps:  # noqa: SIM110
            if app_name in app:
                return True
        return False
    except subprocess.CalledProcessError as e:
        if log:
            log.exception("Error checking Flatpak apps: %s", e)
        return False


def open_url_in_browser(url: str, log: Union[OxtLogger, None] = None) -> None:
    """
    Open the specified URL in the default web browser.

    Args:
        url (str): The URL to open.

    Example:
        .. code-block:: python

            open_url_in_browser("https://www.example.com")
    """

    try:
        import webbrowser

        if log:
            log.info("Opening URL '%s' in web browser", url)

        webbrowser.open(url)
    except Exception as e:
        if log:
            log.exception(f"Error opening URL {url}: {e}")
