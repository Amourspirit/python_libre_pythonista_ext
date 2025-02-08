from __future__ import annotations
from typing import cast, TYPE_CHECKING
from urllib.parse import parse_qs
from ooodev.calc import CalcCell, CalcSheet
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.exceptions import ex as mEx  # noqa: N812
from ooodev.calc import CellObj
from ..dispatch.cell_dispatch_state import CellDispatchState
from .ctl.ctl_mgr import CtlMgr
from .props.key_maker import KeyMaker
from .state.ctl_state import CtlState
from .state.state_kind import StateKind
from ..const import DISPATCH_PY_OBJ_STATE, DISPATCH_DF_STATE
from ..cell.result_action.pyc.rules.pyc_rules import PycRules
from ..code.py_source_mgr import PySource, PyInstance
from ..utils.pandas_util import PandasUtil
from ..menus import menu_util as mu


if TYPE_CHECKING:
    from com.sun.star.drawing import XControlShape
    from ooodev.draw.shapes.draw_shape import DrawShape
    from ooodev.calc.spreadsheet_draw_page import SpreadsheetDrawPage
    from .ctl.ctl_rule_t import CtlRuleT
    from ..cell.result_action.pyc.rules.pyc_rule_t import PycRuleT
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class LplCell:
    """
    Represents a cell in a spreadsheet that is a Libre Pythonista cell.

    It is possible the state may change and the cell may no longer be a Libre Pythonista cell or have valid settings.
    For this reason it is important to call ``refresh()`` of the cell before using stored instances.
    """

    def __init__(self, cell: CalcCell) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug("Creating LplCell(%s)", cell.cell_obj)
        self._cell = cell
        self._cell_dispatch_state = CellDispatchState(cell)
        self._key_maker = KeyMaker()
        self._ctl_mgr = CtlMgr()
        self._pyc_rules = PycRules()
        self._pyc_src_mgr = PyInstance(self._cell.calc_doc)  # singleton
        self._cache = {}

    # region dunder method
    def __repr__(self) -> str:
        return f"<LplCell({self.cell.cell_obj})>"

    # endregion dunder method

    # region Methods
    def remove_control(self) -> None:
        with self._log.indent(True):
            """Removes the control from the cell if it exist."""
            self._log.debug("remove_control() Entered")
            if not self.ctl_shape_name:
                self._log.debug("remove_control() No control shape name found. Returning")
                return
            self._ctl_mgr.remove_ctl(self.cell)
            self._log.debug("remove_control() Control removed")
            self.refresh()
            self._log.debug("remove_control() Done.")

    def update_control(self) -> None:
        """
        Update the control for a cell when the cell is modified.
        This may mean the the control get changed or removed.

        There is not need to call ``RemoveControl()`` before calling this method.
        """
        with self._log.indent(True):
            self._log.debug("update_control() Entered")

            if self.ctl_state == StateKind.ARRAY:
                self._log.debug("update_control() State is ARRAY. removing control")
                self.remove_control()
                return
            matched_rule = self._pyc_rules.get_matched_rule(cell=self.cell, data=self.pyc_src.dd_data)

            if matched_rule is None:
                self._log.debug("update_control() No matched rule found. Removing any existing control")
                self.remove_control()
                self._log.debug("update_control() Done")
                return
            self._log.debug("_update_py_event_control() Matched rule: %s", matched_rule.name)
            # matched_rule.name is a cell.props.rule_names.RuleNames value.
            # set the pyc rule key custom property for the cell.
            # let update handle removing and adding new control
            self.cell.set_custom_property(self._key_maker.pyc_rule_key, matched_rule.name)
            self._ctl_mgr.update_ctl(self.cell)
            self.refresh()
            self._log.debug("update_control() Done")

    def get_dispatch_command(self, url_main: str) -> str:
        """
        Gets a dispatch command when the url main is given.

        Args:
            url_main (str): The main url to use such as ``.uno:libre_pythonista.calc.menu.code.df.state``.

        Returns:
            str: The dispatch command with the cell and sheet information.
        """
        return f"{url_main}?sheet={self.cell.calc_sheet.name}&cell={self.cell.cell_obj}"

    def get_control_rule(self) -> CtlRuleT | None:
        """Get a control rule instance for the cell"""
        with self._log.indent(True):
            try:
                ct = self._ctl_mgr.get_current_ctl_type_from_cell(self.cell)
                if ct is None:
                    return None
                return ct(self.cell)
            except Exception:
                self._log.error("get_control_rule() Error getting control rule", exc_info=True)

    def get_control_supports_feature(self, feature: str) -> bool:
        """
        Checks if the feature is supported by the control.

        Args:
            feature (str): Feature to check such as "update_ctl", "add_ctl", "remove_ctl", "update_ctl_action", "get_rule_name", "get_cell_pos_size".

        Returns:
            bool: True if supported, False otherwise.
        """
        with self._log.indent(True):
            try:
                rule = self.get_control_rule()
                if rule is None:
                    return False
                return rule.supports_feature(feature)
            except Exception:
                self._log.error("get_control_supports_feature() Error getting control supports feature", exc_info=True)
        return False

    def _convert_query_to_dict(self, query: str) -> dict:
        query_dict = parse_qs(query)
        return {k: v[0] for k, v in query_dict.items()}

    def _get_control_shape(self) -> DrawShape[SpreadsheetDrawPage[CalcSheet]] | None:
        """
        Gets the control shape of the cell.

        Returns:
            XControlShape | None: The control shape or None if not found.
        """
        with self._log.indent(True):
            try:
                shape_name = self.ctl_shape_name
                if not shape_name:
                    return None
                dp = self.cell.calc_sheet.draw_page
                try:
                    shape = dp.find_shape_by_name(shape_name)
                except mEx.ShapeMissingError:
                    shape = None
                return shape  # type: ignore
            except Exception:
                self._log.error("get_control_shape() Error getting control shape", exc_info=True)
                return None

    def _get_pyc_src(self) -> PySource:
        with self._log.indent(True):
            """Gets the python source of the cell."""
            try:
                return self._pyc_src_mgr[self.cell.cell_obj]
            except Exception:
                self._log.error("get_pyc_src() Error getting python source", exc_info=True)
                raise

    def refresh(self) -> None:
        self._cache.clear()

    def _dispatch_command(self, url_main: str) -> None:
        """Dispatches a command to the cell."""
        url = mu.get_url_from_command(url_main)
        mu.dispatch_cs_cmd(cmd=url_main, in_thread=False, url=url, log=self._log)

    # endregion Methods

    # region Reset Methods
    def reset_py_instance(self) -> None:
        """Resets the PyInstance."""
        PyInstance.reset_instance(doc=self.cell.calc_doc)
        self.refresh()

    # endregion Reset Methods

    # region Properties
    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def ctl_state(self) -> StateKind:
        """
        Get/Sets the state of the control. If the state is unknown, return ``StateKind.UNKNOWN``.

        Setting this value will also update the Calc Cell to reflect the change.

        If the current state is ``ARRAY`` and the new state is unknown, the state is changed to ``PY_OBJ``.

        The cell control is not directly changed by this property but can by changed by other listeners as a result of dispatching a command.

        This is a cached property.
        """
        key = "ctl_state"
        if key in self._cache:
            return self._cache[key]
        try:
            state = CtlState(self.cell).get_state()
        except Exception:
            state = StateKind.UNKNOWN
        self._cache[key] = state
        return state

    @ctl_state.setter
    def ctl_state(self, value: StateKind) -> None:
        with self._log.indent(True):
            self._log.debug("ctl_state Setting state to %s", value)
            current_state = self.ctl_state
            self._log.debug("ctl_state Current state is %s", current_state)
            if current_state == value:
                return
            key = "ctl_state"
            self._cache[key] = value
            if value == StateKind.UNKNOWN:
                self._log.debug("ctl_state State is unknown.")
                if current_state == StateKind.ARRAY:
                    self._log.debug("ctl_state Current state is ARRAY. Dispatching command to change to PY_OBJ")
                    # if the new value is unknown and the current state is array, then dispatch the command
                    # that converts it back to PY_OBJ.
                    pyc_rule = self.pyc_rule
                    if pyc_rule is None:
                        return
                    # url_main = pyc_rule.get_dispatch_state()
                    url_main = DISPATCH_PY_OBJ_STATE
                    cmd = self.get_dispatch_command(url_main)
                    # self.cell.calc_doc.dispatch_cmd(cmd)
                    self._dispatch_command(cmd)
                self._ctl_mgr.remove_ctl(self.cell)
                return
            if value == StateKind.ARRAY and current_state != StateKind.ARRAY:
                self._log.debug("ctl_state Setting state to ARRAY")
                # the current state is not array
                # Set the state to py obj first and then call the dispatch command.
                # The dispatch command will toggle from PY_OBJ to ARRAY.
                # Optionally the dispatch could be call twice.
                self._log.debug("ctl_state Removing control if it exist")
                self._ctl_mgr.remove_ctl(self.cell)
                self._log.debug("ctl_state Setting state to PY_OBJ")
                cs = CtlState(cell=self.cell)
                cs.set_state(StateKind.PY_OBJ)
                url_main = self.cell_dispatch_state.get_rule_dispatch_cmd()
                # url_main = DISPATCH_DF_STATE
                if not url_main:
                    self._log.error("ctl_state No dispatch command found. Returning")
                    return
                cmd = self.get_dispatch_command(url_main)
                self._log.debug("ctl_state Dispatching command: %s", cmd)
                # self.cell.calc_doc.dispatch_cmd(cmd)
                self._dispatch_command(cmd)
                return
            # a known value
            # if there is a rule and a dispatch the toggle the state with a dispatch.
            pyc_rule = self.pyc_rule
            if pyc_rule is None:
                self._log.debug("ctl_state No rule found. Returning")
                return
            # url_main = pyc_rule.get_dispatch_state()
            url_main = DISPATCH_PY_OBJ_STATE
            if not url_main:
                self._log.debug("ctl_state No dispatch command found. Returning")
                return
            cmd = self.get_dispatch_command(url_main)
            self._log.debug("ctl_state Dispatching command: %s", cmd)
            # dispatch will change the state to StateKind.PY_OBJ if it is not already.
            # self.cell.calc_doc.dispatch_cmd(cmd)
            self._dispatch_command(cmd)
            ctl_state_obj = CtlState(self.cell)
            ctl_state = ctl_state_obj.get_state()
            if ctl_state == value:
                return
            ctl_state_obj.set_state(value)

    @property
    def custom_properties(self) -> DotDict:
        """
        Gets the custom properties of the cell.

        This is a cached property.
        """
        with self._log.indent(True):
            key = "custom_properties"
            if key in self._cache:
                return self._cache[key]
            try:
                cp = self.cell.get_custom_properties()
                self._cache[key] = cp
                return cp
            except Exception:
                self._log.error("custom_properties() Error getting custom properties", exc_info=True)
                return DotDict()

    @property
    def is_dataframe(self) -> bool:
        """
        Get if the cell is a dataframe.
        """
        src = self.pyc_src
        if src.dd_data is None:
            return False
        if "data" in src.dd_data:
            return PandasUtil.is_dataframe(src.dd_data.data)
        return False

    @property
    def is_table_data(self) -> bool:
        """
        Get if the cell is a Table Data.
        """
        return self.pyc_rule_name == self._key_maker.rule_names.cell_data_type_tbl_data

    @property
    def pyc_rule_name(self) -> str:
        """
        Get/Sets the pyc rule of the control. If the rule is not found, return an empty string.
        """
        key = self._key_maker.pyc_rule_key
        if key in self.custom_properties:
            return self.custom_properties[key]
        return ""

    @pyc_rule_name.setter
    def pyc_rule_name(self, value: str) -> None:
        key = self._key_maker.pyc_rule_key
        self.cell.set_custom_property(key, value)
        if "custom_properties" in self._cache:
            del self._cache["custom_properties"]

    @property
    def pyc_rule(self) -> PycRuleT | None:
        """
        Gets the pyc rule of the cell or None.

        This is a cached property.
        """
        key = "pyc_rule"
        if key in self._cache:
            return self._cache[key]
        rule = self._pyc_rules.find_rule(self.cell)
        self._cache[key] = rule
        return rule

    @property
    def ctl_shape_name(self) -> str:
        """
        Get the shape name of the control from the properties. If the shape name is not found, return an empty string.
        """
        key = self._key_maker.ctl_shape_key
        if key in self.custom_properties:
            return self.custom_properties[key]
        return ""

    @property
    def ctl_shape(self) -> DrawShape[SpreadsheetDrawPage[CalcSheet]] | None:
        """
        Gets the control shape or None.

        This is a cached property.
        """
        key = "control_shape"
        if key in self._cache:
            return self._cache[key]
        shape = self._get_control_shape()
        self._cache[key] = shape
        return shape

    @property
    def ctl_shape_visible(self) -> bool:
        """
        Get/Sets the visibility of the control shape. If the shape is not found, return False.
        """
        with self._log.indent(True):
            shape = self.ctl_shape
            if shape is None:
                return False
            try:
                return shape.component.Visible  # type: ignore
            except Exception:
                self._log.error("ctl_shape_visible() Error getting control shape visibility", exc_info=True)
                return False

    @ctl_shape_visible.setter
    def ctl_shape_visible(self, value: bool) -> None:
        with self._log.indent(True):
            shape = self.ctl_shape
            if shape is None:
                return
            try:
                shape.set_visible(value)
            except Exception:
                self._log.error("ctl_shape_visible() Error setting control shape visibility", exc_info=True)

    @property
    def pyc_src(self) -> PySource:
        """
        Get the python source of the cell.

        This is a cached property.
        """
        key = "pyc_src"
        if key in self._cache:
            return self._cache[key]
        src = self._get_pyc_src()
        self._cache[key] = src
        return src

    @property
    def cell_prop_addr(self) -> CellObj:
        """
        Get/Set the cell address of the cell from the custom property.

        If there is no custom property for the cell then the current cell is returned.
        If needed use with ``has_address_prop`` to check if the cell has an address property.

        This is a cached property.
        """
        with self._log.indent(True):
            key = "pyc_src"
            if key in self._cache:
                return self._cache[key]
            addr_key = self._key_maker.cell_addr_key
            if addr_key not in self.custom_properties:
                self._log.warning(
                    "cell_prop_addr() Cell address not found in custom properties. Returning current cell."
                )
                return self._cell.cell_obj
            try:
                addr = cast(str, self.custom_properties[addr_key])
                # addr is in format of sheet_index=0&cell_addr=A1
                d = self._convert_query_to_dict(addr)
                idx = int(d.get("sheet_index", "-2"))
                cell_obj = CellObj.from_cell(cast(str, d["cell_addr"]))
                result = CellObj(col=cell_obj.col, row=cell_obj.row, sheet_idx=idx)
                self._cache[key] = result
                return result
            except Exception:
                self._log.exception("cell_prop_addr() Error getting cell address from custom properties.")
            return self._cell.cell_obj

    @cell_prop_addr.setter
    def cell_prop_addr(self, value: CellObj) -> None:
        key = self._key_maker.cell_addr_key
        addr = f"sheet_index={value.sheet_idx}&cell_addr={value}"
        self.cell.set_custom_property(key, addr)
        if "custom_properties" in self._cache:
            del self._cache["custom_properties"]

    @property
    def has_address_prop(self) -> bool:
        """
        Get if the cell has an address property.
        """
        key = self._key_maker.cell_addr_key
        return key in self.custom_properties

    @property
    def has_cell_moved(self) -> bool:
        """
        Get if the cell has moved.
        """
        if not self.has_address_prop:
            return False
        return self.cell.cell_obj != self.cell_prop_addr

    @property
    def has_pyc_src(self) -> bool:
        """
        Get if the cell has a python source.
        """
        try:
            _ = self.pyc_src
            return True
        except Exception:
            return False

    @property
    def has_code_name_prop(self) -> bool:
        """
        Get if the cell has a code name property.
        """
        key = self._key_maker.cell_code_name
        return key in self.custom_properties

    @property
    def has_array_ability(self) -> bool:
        """
        Get/Sets whether the cell has the ability to be an array.
        """
        key = self._key_maker.cell_array_ability_key
        if key in self.custom_properties:
            return bool(self.custom_properties[key])
        return False

    @property
    def cell_dispatch_state(self) -> CellDispatchState:
        """Cell Dispatch State. Class to get the dispatch state of a cell."""
        return self._cell_dispatch_state

    # endregion Properties
