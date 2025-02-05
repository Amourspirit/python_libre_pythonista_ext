from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator
from ooodev.loader.inst.doc_type import DocType

from ...const import (
    DISPATCH_PY_CODE_VALIDATE,
    DISPATCH_SEL_RNG,
    DISPATCH_SEL_LP_FN,
)


if TYPE_CHECKING:
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DialogMbMenu:
    """Dialog Menu Builder"""

    def __init__(self, dlg: Any) -> None:  # noqa: ANN401
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("init")
        self._dlg = dlg
        self._doc = dlg.doc
        self._is_calc_doc = self._doc.DOC_TYPE == DocType.CALC
        self._log.debug(f"init() Done: is_calc_doc: {self._is_calc_doc}")

    def get_insert_menu(self) -> PopupMenu:
        self._log.debug("get_insert_menu()")
        try:
            menu_data = self._get_insert_data()
            popup_creator = PopupCreator()
            popup_menu = popup_creator.create(menu_data)
            return popup_menu
        except Exception:
            self._log.exception("get_insert_menu()")
            raise

    def get_code_menu(self) -> PopupMenu:
        self._log.debug("get_code_menu()")
        try:
            menu_data = self._get_code_data()
            popup_creator = PopupCreator()
            popup_menu = popup_creator.create(menu_data)
            return popup_menu
        except Exception:
            self._log.exception("get_code_menu()")
            raise

    def _get_insert_data(self) -> List[dict]:
        self._log.debug("_get_insert_data()")
        try:
            rr = self._dlg.res_resolver.resolve_string

            new_menu = [
                {
                    "text": rr("mnuAutoLpFn"),
                    "command": DISPATCH_SEL_LP_FN,
                },
                {
                    "text": rr("mnuSelectRng"),
                    "command": DISPATCH_SEL_RNG,
                },
            ]
            return new_menu
        except Exception:
            self._log.exception("_get_insert_data()")
            raise

    def _get_code_data(self) -> List[dict]:
        self._log.debug("_get_code_data()")
        try:
            rr = self._dlg.res_resolver.resolve_string

            # new_menu = [
            #     {
            #         "text": rr("mnuData"),
            #         "command": ".uno.py_data",
            #         "submenu": [
            #             {"text": rr("mnuValidate"), "command": DISPATCH_PY_CODE_VALIDATE},
            #         ],
            #     }
            # ]
            new_menu = [
                {
                    "text": rr("mnuValidate"),
                    "command": DISPATCH_PY_CODE_VALIDATE,
                }
            ]
            return new_menu
        except Exception:
            self._log.exception("_get_code_data()")
            raise
