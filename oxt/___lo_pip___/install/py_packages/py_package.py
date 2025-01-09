from __future__ import annotations
from typing import Any, cast, Dict, Set, Tuple


class PyPackage:
    """General INstallation rules for a package."""

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Initialize the package with the given keyword arguments.
        Args:
            **kwargs: Arbitrary keyword arguments.
                - name (str, optional): The name of the package.
                - version (str, optional): The version of the package.
                - restriction (str, optional): Any restrictions for the package.
                - pkg_type (str, optional): The type of package such as ``lp_editor_py_packages`` or ``py_packages``.
                - platforms (Iterable, optional): A set of platforms the package supports.
                - ignore_platforms (Iterable, optional): A set of platforms to ignore.
                - python_versions (Iterable, optional): A set of Python versions the package supports.
        """

        self._name = cast(str, kwargs.get("name", ""))
        self._version = cast(str, kwargs.get("version", ""))
        self._restriction = cast(str, kwargs.get("restriction", ">="))
        self._pkg_type = cast(str, kwargs.get("pkg_type", ""))
        self._platforms = set(kwargs.get("platforms", ["all"]))
        self._ignore_platforms = set(kwargs.get("ignore_platforms", []))
        self._python_versions = set(kwargs.get("python_versions", []))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({self.name} {self.restriction} {self.version} {self.platforms} {self.ignore_platforms} {self.python_versions})>"

    def __copy__(self) -> PyPackage:
        return self.copy()

    def is_platform(self, platform: str) -> bool:
        """
        Checks if the specified platforms is supported.

        If the value is in the ignore platforms, the method will return False.

        Args:
            platform (str): The operating system to check. If the value is "all", the method will return True.
                Values can be ``win``, ``mac``, ``linux``, ``all``.

        Returns:
            bool: True if the operating system is supported or if the value is "all", otherwise False.
        """
        if "all" in self.platforms:
            return True

        if platform in self.ignore_platforms:
            return False
        return platform in self.platforms

    def is_ignored_platform(self, platform: str) -> bool:
        """
        Checks if the specified operating system is ignored.

        Args:
            platform (str): The operating system to check. Values can be ``win``, ``mac``, ``linux``, ``flatpak``, ``snap``.

        Returns:
            bool: True if the operating system is ignored, otherwise False.
        """
        return platform in self.ignore_platforms

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the current instance to a dictionary.

        Returns:
            Dict[str, str]: A dictionary containing the package information.
        """
        return {
            "name": self.name,
            "version": self.version,
            "restriction": self.restriction,
            "pkg_type": self._pkg_type,
            "platforms": list(self.platforms),
            "ignore_platforms": list(self.ignore_platforms),
            "python_versions": list(self.python_versions),
        }

    def copy(self) -> PyPackage:
        """
        Creates a copy of the current instance.

        Returns:
            PyPackage: A copy of the current instance.
        """
        gi = PyPackage()
        gi.name = self.name
        gi.version = self.version
        gi.restriction = self.restriction
        gi.pkg_type = self.pkg_type
        gi.platforms = self.platforms.copy()
        gi.ignore_platforms = self.ignore_platforms.copy()
        gi.python_versions = self.python_versions.copy()
        return gi

    @classmethod
    def from_dict(cls, **kwargs: Any) -> PyPackage:  # noqa: ANN401
        """
        Creates an instance of PyPackage from a dictionary.

        Keyword Arguments:
            name (str): The name of the installation. Defaults to an empty string if not provided.
            version (str): The version of the installation. Defaults to an empty string if not provided.
            restriction (str, optional): The restriction for the installation. Defaults to ">=" if not provided.
            platforms (list, optional): A list of platforms for the installation. Defaults to ["all"] if not provided.
            ignore_platforms (list, optional): A list of platforms to ignore for the installation. Defaults to an empty list if not provided.
            python_versions (list, optional): A list of python versions for the installation. Defaults to an empty list if not provided.

        Returns:
            PyPackage: An instance of PyPackage initialized with the provided data.
        """

        gi = cls()
        gi.name = cast(str, kwargs.get("name", ""))
        gi.version = cast(str, kwargs.get("version", ""))
        gi.restriction = cast(str, kwargs.get("restriction", gi.restriction))
        gi.pkg_type = cast(str, kwargs.get("pkg_type", gi.pkg_type))
        gi.platforms = set(kwargs.get("platforms", gi.platforms))
        gi.ignore_platforms = set(kwargs.get("ignore_platforms", gi.ignore_platforms))
        gi.python_versions = set(kwargs.get("python_versions", gi.python_versions))
        return gi

    def __hash__(self) -> int:
        return hash(
            (
                self.name,
                self.version,
                self.restriction,
                self.pkg_type,
                frozenset(self.platforms),
                frozenset(self.ignore_platforms),
                frozenset(self.python_versions),
            )
        )

    # region Properties
    @property
    def name(self) -> str:
        """Gets/sets the name of the package."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def version(self) -> str:
        """
        Gets/sets the version of the package such as ``1.0.0``.

        Note:
            For wildcard version, use ``*`` and set restriction to ``==``.
        """
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    @property
    def restriction(self) -> str:
        """
        Gets/sets the restriction such as ``>=``.

        Acceptable values include ``==``, ``>=``, ``<=``, ``>``, ``<``, ``~=``, ``~``, ``^``.

        Note:
            For wildcard version, use ``==`` and set version to ``*``.
        """
        return self._restriction

    @restriction.setter
    def restriction(self, value: str) -> None:
        self._restriction = value

    @property
    def platforms(self) -> Set[str]:
        return self._platforms

    @platforms.setter
    def platforms(self, value: Set[str]) -> None:
        """
        Sets the platforms for the installation rules.

        Platforms can be ``win``, ``mac``, ``linux`` or ``all``.

        Args:
            value (Set[str]): A set of platform names to be set.
        """

        self._platforms = value

    @property
    def ignore_platforms(self) -> Set[str]:
        """
        Returns a set of platform names that should be ignored during the installation process.

        Ignore platforms can be ``win``, ``mac``, ``linux``, ``flatpak`` or ``snap``.

        Returns:
            Set[str]: A set of platform names to be ignored.
        """

        return self._ignore_platforms

    @ignore_platforms.setter
    def ignore_platforms(self, value: Set[str]) -> None:
        self._ignore_platforms = value

    @property
    def python_versions(self) -> Set[str]:
        """
        Gets the python versions for the installation rules.

        A single version in the set can be ``==3.8``, ``>=3.9``, ``<3.10`` or ``<=3.2``.

        Returns:
            Set[str]: A set of python versions.
        """
        return self._python_versions

    @python_versions.setter
    def python_versions(self, value: Set[str]) -> None:
        self._python_versions = value

    @property
    def pip_install(self) -> Dict[str, str]:
        """
        Gets the pip install command for the package such as ``{'verr': '>=1.1.2'``.

        Returns:
            Dict[str, str]: The pip install command for the package.
        """
        return {self.name: f"{self.restriction}{self.version}"}

    @property
    def name_version(self) -> Tuple[str, str]:
        """
        Gets the name and version of the package.

        Returns:
            Tuple[str, str]: A tuple containing the name and version of the package.
        """
        return self.name, f"{self.restriction}{self.version}"

    @property
    def pkg_type(self) -> str:
        """
        Gets/sets the package type such as ``lp_editor_py_packages`` or ``py_packages``.

        Returns:
            str: The package type.
        """
        return self._pkg_type

    @pkg_type.setter
    def pkg_type(self, value: str) -> None:
        self._pkg_type = value

    # endregion Properties
