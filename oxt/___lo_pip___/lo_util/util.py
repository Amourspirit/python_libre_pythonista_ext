from __future__ import annotations
from typing import Any
import uno
from pathlib import Path

from ..meta.singleton import Singleton


class Util(metaclass=Singleton):
    """Utility Functions."""

    def create_uno_service(self, service: str, *, ctx: Any = None, args: Any = None) -> Any:
        """
        Creates an instance of a UNO service.

        Args:
            service (str): Service Name
            ctx (Any, optional): Component Context. Defaults to None.
            args (Any, optional): Args. Defaults to None.

        Returns:
            Any: New instance of service.
        """
        if not ctx:
            ctx = uno.getComponentContext()
        service_mgr = ctx.getServiceManager()  # type: ignore
        if ctx and args:
            return service_mgr.createInstanceWithArgumentsAndContext(service, args, ctx)
        elif args:
            return service_mgr.createInstanceWithArguments(service, args)
        elif ctx:
            return service_mgr.createInstanceWithContext(service, ctx)
        else:
            return service_mgr.createInstance(service)

    def config(self, name="Work"):
        """
        Return the path name in config
        http://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1util_1_1XPathSettings.html

        Examples:

            ``config("module")``
            ``/usr/lib/libreoffice/program``

            ``config("Work")``
            ``/home/user/Documents``
        """
        path = self.create_uno_service("com.sun.star.util.PathSettings")
        return self.to_system(getattr(path, name))

    def to_system(self, path: str) -> str:
        if path.startswith("file://"):
            path = str(Path(uno.fileUrlToSystemPath(path)).resolve())
        return path
