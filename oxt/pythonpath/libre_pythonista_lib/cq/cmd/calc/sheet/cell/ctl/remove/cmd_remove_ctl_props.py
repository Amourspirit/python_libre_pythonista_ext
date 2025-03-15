from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast, Dict, Set, Sequence

# Conditional imports for type checking and runtime
if TYPE_CHECKING:
    # Type checking imports
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames
else:
    # Runtime imports
    from libre_pythonista_lib.utils.null import NULL
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.common.prop.qry_prop_names import QryPropNames

    CalcCell = Any


# tested in: tests/test_cmd/test_cmd_remove_ctl_props.py


class CmdRemoveCtlProps(CmdBase, LogMixin, CmdT):
    """
    Command class for removing control properties from a cell.
    Implements the Command pattern with undo functionality.
    """

    def __init__(self, ctl: Ctl) -> None:
        """
        Initialize the command with a control instance.

        Args:
            ctl: Control instance containing cell and property information
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._removed: Dict[str, Any] = {}

    def _validate(self) -> bool:
        """
        Validates that the control has required attributes.

        Returns:
            bool: True if validation passes, False otherwise
        """
        required_attributes = {"cell", "ctl_props"}

        # make a copy of the ctl dictionary because will always return True
        # when checking for an attribute directly.
        ctl_dict = self._ctl.copy_dict()

        for attrib in required_attributes:
            if not attrib in ctl_dict:
                self.log.error("Validation error. %s attribute is missing.", attrib)
                return False
        return True

    def _get_ctl_props(self) -> Set[str]:
        """
        Gets the control property names that are set for the cell custom properties.

        Returns:
            Set[str]: Set of property names
        """
        props = cast(Sequence[CtlPropKind], self._ctl.ctl_props)
        if not props:
            return set()
        qry = QryPropNames(*props)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Executes the command to remove control properties.
        Stores removed properties for potential undo operation.
        """
        self.success = False
        self._removed.clear()
        if not self._validate():
            self.log.error("Validation error occurred. Unable to execute command.")
            return
        try:
            cell = cast(CalcCell, self._ctl.cell)
            prop_names = self._get_ctl_props()
            for name in prop_names:
                value = cell.get_custom_property(name, NULL)
                if value is NULL:
                    continue

                cell.remove_custom_property(name)
                self._removed[name] = value

        except Exception:
            self.log.exception("Error inserting control")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to restore previously removed properties.
        """
        if not self._removed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        try:
            cell = cast(CalcCell, self._ctl.cell)
            for name, value in self._removed.items():
                cell.set_custom_property(name, value)
            self._removed.clear()
        except Exception:
            self.log.exception("Error undoing custom properties")
            return
        self.log.debug("Successfully executed undo command.")

    @override
    def undo(self) -> None:
        """
        Public method to undo the command if it was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")
