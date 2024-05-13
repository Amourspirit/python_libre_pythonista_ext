from __future__ import annotations
import uno
from typing import Any, cast, TYPE_CHECKING

from ..config import Config
from ..oxt_logger import OxtLogger

from com.sun.star.lang import Locale
from com.sun.star.resource import MissingResourceException

if TYPE_CHECKING:
    from com.sun.star.util import PathSubstitution  # service
    from com.sun.star.resource import StringResourceWithLocation  # service


class ResourceResolver:
    """Resource Resolver for localized strings"""

    def __init__(self, ctx: Any):
        self._config = Config()
        self._logger = OxtLogger(log_name=__name__)
        try:
            self.ctx = ctx
            self.service_manager = self.ctx.getServiceManager()
            self.locale = self._get_env_locale()
            self.resource_resolver = self._get_resource_resolver(self.locale)
            self.version = self._get_ext_ver()
            self._default_resource_resolver: StringResourceWithLocation | None = None

            # config.default_locale can be 1 to 3 parts
            locale_parts = self._config.default_locale + 2 * [""]
            self._default_locale = Locale(*locale_parts[:3])

            if not self._is_default_locale():
                self._logger.debug(f"ResourceResolver.__init__: locale={self.locale}")
                self._default_resource_resolver = self._get_resource_resolver(self._default_locale)
        except Exception as err:
            self._logger.error(f"ResourceResolver.__init__: {err}", exc_info=True)

    def _is_default_locale(self) -> bool:
        """Check if the current locale is the default locale"""

        return (
            self.locale.Language == self._default_locale.Language
            and self.locale.Country == self._default_locale.Country
            and self.locale.Variant == self._default_locale.Variant
        )

    def _get_ext_ver(self) -> str:
        """Get addon version number"""
        info = self._config.extension_info.get_extension_info(self._config.lo_implementation_name)
        try:
            return info[1]
        except Exception:
            return "0.0.0"

    def _get_env_locale(self):
        """Get interface locale"""
        ps = cast(
            "PathSubstitution",
            self.service_manager.createInstanceWithContext("com.sun.star.util.PathSubstitution", self.ctx),
        )
        v_lang = ps.getSubstituteVariableValue("vlang")
        # self._logger.debug(f"ResourceResolver._get_env_locale: v_lang={v_lang}")
        a_lang = v_lang.split("-") + 2 * [""]
        # self._logger.debug(f"ResourceResolver._get_env_locale: a_lang={a_lang}")
        return Locale(*a_lang[:3])

    def _get_resource_resolver(self, locale: Locale) -> StringResourceWithLocation:
        # url = self._get_ext_path() + "python"
        url = f"vnd.sun.star.extension://{self._config.lo_identifier}/{self._config.resource_dir_name}"
        handler = self.service_manager.createInstanceWithContext("com.sun.star.task.InteractionHandler", self.ctx)
        return cast(
            "StringResourceWithLocation",
            self.service_manager.createInstanceWithArgumentsAndContext(
                "com.sun.star.resource.StringResourceWithLocation",
                (url, False, locale, self._config.resource_properties_prefix, "", handler),
                self.ctx,
            ),
        )

    def resolve_string(self, id: str) -> str:
        """Resolve localized string

        Args:
            id (str): resource id

        Returns:
            str: localized string
        """
        if id == "empty":
            return ""
        try:
            return self.resource_resolver.resolveString(id)
        except MissingResourceException:
            # resource is not in the current locale get it from the default locale
            if self._default_resource_resolver:
                return self._default_resource_resolver.resolveString(id)
        except Exception as err:
            self._logger.error(f"ResourceResolver.resolve_string: {err}", exc_info=True)
            return id
        self._logger.error(f"ResourceResolver.resolve_string missing resource for: {id}")
        return id
