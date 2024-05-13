# coding: utf-8
from __future__ import annotations, unicode_literals
import sys
from typing import Any, TYPE_CHECKING, cast
from enum import Enum
from pathlib import Path
import uno
import getpass, os, os.path
from ..meta.singleton import Singleton


# com.sun.star.uno.DeploymentException

if TYPE_CHECKING:
    from com.sun.star.util import PathSubstitution  # service


class PathKind(Enum):
    """Kind of path to register"""

    SHARE_PYTHON = 1
    SHARE_USER_PYTHON = 2


class RegisterPathKind(Enum):
    """Kind of path to register"""

    REGISTERED = 1
    ALREADY_REGISTERED = 2
    NOT_REGISTERED = 3


class UnRegisterPathKind(Enum):
    """Kind of path to unregister"""

    UN_REGISTERED = 1
    ALREADY_UN_REGISTERED = 2
    NOT_UN_REGISTERED = 3


# class Session(metaclass=Singleton):
#     pass


class Session(metaclass=Singleton):
    """
    Session Class for handling user paths within the LibreOffice environment.

    See Also:
        - `Importing Python Modules <https://help.libreoffice.org/latest/lo/text/sbasic/python/python_import.html>`_
        - `Getting Session Information <https://help.libreoffice.org/latest/lo/text/sbasic/python/python_session.html>`_
    """

    # https://help.libreoffice.org/latest/lo/text/sbasic/python/python_import.html
    # https://help.libreoffice.org/latest/lo/text/sbasic/python/python_session.html

    @property
    def path_sub(self) -> PathSubstitution:
        try:
            return self._path_substitution  # type: ignore
        except AttributeError:
            ctx: Any = uno.getComponentContext()
            self._path_substitution = cast(
                "PathSubstitution", ctx.ServiceManager.createInstance("com.sun.star.util.PathSubstitution")
            )
        return self._path_substitution  # type: ignore

    def substitute(self, var_name: str):
        """
        Returns the current value of a variable.

        The method iterates through its internal variable list and tries to find the given variable.
        If the variable is unknown a com.sun.star.container.NoSuchElementException is thrown.

        Args:
            var_name (str): name to search for.

        Raises:
            com.sun.star.container.NoSuchElementException: ``NoSuchElementException``
        """
        return self.path_sub.getSubstituteVariableValue(var_name)

    @property
    def share(self) -> str:
        """
        Gets Program Share dir,
        such as ``C:\\Program Files\\LibreOffice\\share``
        """
        try:
            return self._share
        except AttributeError:
            inst = uno.fileUrlToSystemPath(self.substitute("$(prog)"))
            self._share = os.path.normpath(inst.replace("program", "share"))
        return self._share

    @property
    def shared_scripts(self) -> str:
        """
        Gets Program Share scripts dir,
        such as ``C:\\Program Files\\LibreOffice\\share\\Scripts``
        """
        return "".join([self.share, os.sep, "Scripts"])

    @property
    def shared_py_scripts(self) -> str:
        """
        Gets Program Share python dir,
        such as ``C:\\Program Files\\LibreOffice\\share\\Scripts\\python``
        """
        # eg: C:\Program Files\LibreOffice\share\Scripts\python
        return "".join([self.shared_scripts, os.sep, "python"])

    @property  # alternative to '$(username)' variable
    def user_name(self) -> str:
        """Get the username from the environment or password database.

        First try various environment variables, then the password
        database.  This works on Windows as long as USERNAME is set.
        """
        return getpass.getuser()

    @property
    def user_profile(self) -> str:
        """
        Gets path to user profile such as,
        ``C:\\Users\\user\\AppData\\Roaming\\LibreOffice\\4\\user``
        """
        try:
            return self._user_profile
        except AttributeError:
            self._user_profile = uno.fileUrlToSystemPath(self.substitute("$(user)"))
        return self._user_profile

    @property
    def user_scripts(self) -> str:
        """
        Gets path to user profile scripts such as,
        ``C:\\Users\\user\\AppData\\Roaming\\LibreOffice\\4\\user\\Scripts``
        """
        return "".join([self.user_profile, os.sep, "Scripts"])

    @property
    def user_py_scripts(self):
        """
        Gets path to user profile python such as,
        ``C:\\Users\\user\\AppData\\Roaming\\LibreOffice\\4\\user\\Scripts\\python``
        """
        # eg: C:\Users\user\AppData\Roaming\LibreOffice\4\user\Scripts\python
        return "".join([self.user_scripts, os.sep, "python"])

    def register_path_kind(self, path: PathKind, append: bool = False) -> None:
        """
        Registers a path into ``sys.path`` if it does not exist

        Args:
            path (PathKind): Type of path to register.
            append (bool, optional): If True, appends to ``sys.path`` otherwise prepends. Defaults to False.
        """
        script_path = ""
        if path == PathKind.SHARE_PYTHON:
            script_path = self.shared_py_scripts
        elif path == PathKind.SHARE_USER_PYTHON:
            script_path = cast(str, self.user_py_scripts)
        if not script_path:
            return
        if script_path not in sys.path:
            if append:
                sys.path.append(script_path)
            else:
                sys.path.insert(0, script_path)

    def register_path(self, pth: str | Path, append: bool = False) -> RegisterPathKind:
        """
        Register a path into ``sys.path`` if it does not exist

        Args:
            pth (str | Path): Path to register.
            append (bool, optional): If True, appends to ``sys.path`` otherwise prepends. Defaults to False.
        """
        if not isinstance(pth, str):
            pth = str(pth)
        if not pth:
            return RegisterPathKind.NOT_REGISTERED
        if pth not in sys.path:
            if append:
                sys.path.append(pth)
            else:
                sys.path.insert(0, pth)
            return RegisterPathKind.REGISTERED
        return RegisterPathKind.ALREADY_REGISTERED

    def unregister_path(self, pth: str | Path) -> UnRegisterPathKind:
        """
        Unregister a path into ``sys.path``

        Args:
            pth (str | Path): Path to unregister.
            append (bool, optional): If True, appends to ``sys.path`` otherwise prepends. Defaults to False.
        """
        if not isinstance(pth, str):
            pth = str(pth)
        if not pth:
            return UnRegisterPathKind.NOT_UN_REGISTERED
        if pth in sys.path:
            sys.path.remove(pth)
            return UnRegisterPathKind.UN_REGISTERED
        return UnRegisterPathKind.ALREADY_UN_REGISTERED
