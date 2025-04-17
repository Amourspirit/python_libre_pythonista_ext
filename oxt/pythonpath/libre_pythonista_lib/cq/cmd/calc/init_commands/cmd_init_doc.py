from __future__ import annotations
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.const import LP_DOCUMENT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_init import CmdDocInit
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_py_module_default import CmdPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_doc_custom_prop import CmdDocCustomProp
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_cell_event_mgr import QryCellEventMgr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_array_event_mgr import QryArrayEventMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_code_sheet_activation_listener import (
        CmdCodeSheetActivation,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_doc_event import CmdDocEvent
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_form_design_mode_off import (
        CmdFormDesignModeOff,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_register_dispatch_interceptor import (
        CmdRegisterDispatchInterceptor,
    )

else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule
    from libre_pythonista_lib.const import LP_DOCUMENT
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_init import CmdDocInit
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_t import CmdDocT
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_lp_doc_json_file import CmdLpDocJsonFile
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_py_module_default import CmdPyModuleDefault
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_register_dispatch_interceptor import CmdRegisterDispatchInterceptor
    from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_code_sheet_activation_listener import CmdCodeSheetActivation
    from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_doc_event import CmdDocEvent
    from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_form_design_mode_off import CmdFormDesignModeOff
    from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_activation import CmdSheetActivation
    from libre_pythonista_lib.cq.cmd.calc.doc.listener.cmd_sheet_modified import CmdSheetsModified
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.cmd.doc.cmd_doc_custom_prop import CmdDocCustomProp
    from libre_pythonista_lib.cq.qry.calc.doc.qry_cell_event_mgr import QryCellEventMgr
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.cq.qry.calc.doc.qry_array_event_mgr import QryArrayEventMgr
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result

    PyModuleT = Any

_KEY = "libre_pythonista_lib.init.init_doc.InitDoc"


class CmdInitDoc(CmdBase, List[CmdT], LogMixin, CmdDocT):
    """
    Batch Composite command to initialize the document. It is used to execute a series of commands that are necessary for initializing the document.
    """

    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        list.__init__(self)
        LogMixin.__init__(self)
        self.log.debug("init entered for doc %s", doc.runtime_uid)
        self.append(CmdDocCustomProp(doc=doc, name=LP_DOCUMENT, value=True))
        self.append(CmdDocEvent(doc=doc))
        self.append(CmdCodeSheetActivation(doc=doc))
        self.append(CmdSheetsModified(doc=doc))
        self.append(CmdSheetActivation(doc=doc))
        self.append(CmdFormDesignModeOff(doc=doc))
        self.append(CmdLpDocJsonFile(doc=doc))
        self.append(CmdPyModuleDefault(doc=doc, mod=PyModule()))
        self.append(CmdRegisterDispatchInterceptor(doc=doc))
        self.append(CmdDocInit(doc=doc))  # must be last in the list
        self._success_cmds: List[CmdT] = []
        self._doc = doc
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _get_globals(self) -> DocGlobals | None:
        qry = QryDocGlobals()
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data

    def _qry_default_mod(self) -> PyModuleT:
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def _init_queries(self) -> None:
        """
        Initializes the queries for the document.
        """
        mod = self._qry_default_mod()
        qry_py_src_mgr = QryPySrcMgr(doc=self._doc, mod=mod)

        qry_cell_event_mgr = QryCellEventMgr(doc=self._doc, mod=mod)
        qry_array_event_mgr = QryArrayEventMgr(doc=self._doc)
        self._execute_qry(qry_py_src_mgr)
        self._execute_qry(qry_cell_event_mgr)
        self._execute_qry(qry_array_event_mgr)

    @override
    def execute(self) -> None:
        """
        Executes a series of commands as part of a composite command.
        This method retrieves the current document's global state and checks a specific key in the memory cache.
        If the key's value is "1", the method sets the success flag to True and returns immediately.
        Otherwise, it iterates over the commands, executing each one and collecting successful commands.
        If any command fails, it logs the failure, undoes all previously executed commands, and sets the success flag to False.
        If all commands succeed, it sets the success flag to True and updates the memory cache key to "1".
        In case of an unexpected exception, it logs the exception, undoes all executed commands, and sets the success flag to False.

        Returns:
            None: This method does not return anything.
        """

        doc_globals = self._get_globals()
        if doc_globals is None:
            self.log.error("DocGlobals is None. Unable to execute command.")
            return
        key_val = doc_globals.mem_cache[_KEY]
        if key_val == "1":
            self.success = True
            return
        self.success = False
        self._success_cmds.clear()
        try:
            for cmd in self:
                self._execute_cmd(cmd)
                self.success = cmd.success
                if self.success:  # Only add if command was successful
                    self._success_cmds.append(cmd)
                else:
                    self.log.debug("A command failed. Undoing previously executed commands.")
                    break

            if not self.success:
                self.log.debug("Batch command failed.")
                self._undo()
                return
            self._init_queries()
            doc_globals.mem_cache[_KEY] = "1"
        except Exception as e:
            self.log.exception("An unexpected error occurred: %s", e)
            self._undo()
            self.success = False

        if self.success:
            self.log.debug("Successfully executed command.")

    def _undo(self) -> None:
        for cmd in reversed(self._success_cmds):
            self._execute_cmd_undo(cmd)
        self._success_cmds.clear()
        self.success = False  # Reset success flag.
        doc_globals = DocGlobals.get_current()
        doc_globals.mem_cache[_KEY] = "0"

    @override
    def undo(self) -> None:
        """
        Reverses the execution of all previously executed commands.
        This method iterates over the list of executed commands in reverse order,
        calling the `undo` method on each command to revert its effects. After
        all commands have been undone, the list of executed commands is cleared,
        and the success flag is reset. Additionally, the memory cache for the
        current document's global state is updated.

        Returns:
            None: This method does not return anything.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")
