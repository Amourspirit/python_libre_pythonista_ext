```
PythonImpl: trigger() event: pyc_formula_with_dependent
PythonImpl: Python Code
PyImpl: Py: PyImpl init
PyImpl: Py: PyImpl init
PyImpl: pyc entered
PyImpl: pyc - Doc UID: 1
PyImpl: pyc - sheet_num: arg 1
PyImpl: pyc - cell_address: arg $A$1
PyImpl: pyc - args count: 1
PyImpl: pyc - Cell A1 for sheet index 0 has custom properties: False
PyImpl: pyc - py A1 cell has no code
    LplCell: Creating LplCell(A1)
    PycRules: PycRules.__init__() Initializing.
    PycRules: PycRules.__init__() Initialized.
        PySourceManager: add_source() - Adding Source
        PySourceManager: add_source() sheet index: 0 col: 0, row: 0
        PySourceManager: add_source() - Adding Source ID: id_P9u4XP0ZZS2yLp
        PySourceManager: add_source() - Setting custom property: libre_pythonista_addr to sheet_index=0&cell_addr=A1
        PySourceManager: add_source() - inserting for cell A1: sheet index: 0
            CellCache: insert() Inserting Cell: A1 into Sheet Index: 0 with Code Name: id_P9u4XP0ZZS2yLp
            CellCache: _update_indexes() Updating Indexes
            CellCache: _update_indexes() 1 Indexes Updated
        CellCache: insert() Inserted Cell: A1 into Sheet Index: 0 with Code Name: id_P9u4XP0ZZS2yLp
    PySourceManager: add_source() - inserted for cell A1: sheet index: 0
    PySourceManager: add_source() - Last Index, updating from index 0
        PySourceManager: update_from_index(0) Entered.
            PySourceManager: update_all() Entered.
                PyModule: reset_module()
                PyModule: reset_module() done.
                PySourceManager: __getitem__() - Code Cell: (0, 0, 0)
                PySourceManager: __getitem__() - Result Unique Id: id_P9u4XP0ZZS2yLp
                PySourceManager: _update_item() Entered.
                PySourceManager: _update_item() sheet index: 0 col: 0, row: 0
                    PyModule: set_global_var(CURRENT_CELL_ID, id_P9u4XP0ZZS2yLp)
                    PyModule: set_global_var(CURRENT_CELL_OBJ, A1)
                    PyModule: update_with_result()
                    libre_pythonista: CodeRules - get_matched_rule() found match rule: <CodeEmpty()>
                PySourceManager: _update_item() Leaving.
            PySourceManager: update_all() Leaving.
    PySourceManager: Done Adding Source
    CellMgr: reset_py_inst() Resetting PyInstance
        PySourceManager: Init
    PyModule: _init_mod()
    PyModule: _init_mod() done.
        PySourceManager: update_all() Entered.
            PyModule: reset_module()
            PyModule: reset_module() done.
            PySourceManager: __getitem__() - Code Cell: (0, 0, 0)
            PySourceManager: __getitem__() - Result Unique Id: id_P9u4XP0ZZS2yLp
            PySourceManager: _update_item() Entered.
            PySourceManager: _update_item() sheet index: 0 col: 0, row: 0
                PyModule: set_global_var(CURRENT_CELL_ID, id_P9u4XP0ZZS2yLp)
                PyModule: set_global_var(CURRENT_CELL_OBJ, A1)
                PyModule: update_with_result()
                libre_pythonista: CodeRules - get_matched_rule() found match rule: <CodeEmpty()>
            PySourceManager: _update_item() Leaving.
        PySourceManager: update_all() Leaving.
    CellMgr: reset_py_inst() Done
        CodeCellListener: Init
    CellMgr: Added listener to cell: A1 with codename id_P9u4XP0ZZS2yLp.
    CellMgr: get_py_src() Getting PySource for cell: A1
        PySourceManager: __getitem__() - Code Cell: (0, 0, 0)
        PySourceManager: __getitem__() - Result Unique Id: id_P9u4XP0ZZS2yLp
    CellMgr: get_py_src() Got PySource for cell: A1
    PycRules: get_matched_rule() cell: A1. Data Type DotDict
    PycRules: get_matched_rule() Rule <RuleEmpty(A1, <ooodev.utils.helper.dot_dict.DotDict object at 0x7bfb0ca96110>)> matched.
PyImpl: pyc - Matched Rule: <RuleEmpty(A1, <ooodev.utils.helper.dot_dict.DotDict object at 0x7bfb0ca96110>)>
        libre_pythonista: EmptyCtl: add_ctl(): Entered
            libre_pythonista: CellControl: __init__(): Entered
            libre_pythonista: CellControl: __init__(): Exit
        libre_pythonista: EmptyCtl: add_ctl(): Inserted Button: libre_pythonista_ctl_cell_id_P9u4XP0ZZS2yLp
        libre_pythonista: SimpleCtl: set_ctl_script(): Script location: user:uno_packages
        libre_pythonista: SimpleCtl: set_ctl_script(): Script Name: LibrePythonista.oxt|python|scripts|control_handler.py$on_btn_action_preformed
        libre_pythonista: EmptyCtl: add_ctl(): Leaving
PyImpl: pyc - Done
CellMgr: _on_calc_formulas_calculated() Entering.
    CellMgr: reset_py_inst() Resetting PyInstance
        PySourceManager: Init
    PyModule: _init_mod()
    PyModule: _init_mod() done.
        PySourceManager: update_all() Entered.
            PyModule: reset_module()
            PyModule: reset_module() done.
            PySourceManager: __getitem__() - Code Cell: (0, 0, 0)
            PySourceManager: __getitem__() - Result Unique Id: id_P9u4XP0ZZS2yLp
            PySourceManager: _update_item() Entered.
            PySourceManager: _update_item() sheet index: 0 col: 0, row: 0
                PyModule: set_global_var(CURRENT_CELL_ID, id_P9u4XP0ZZS2yLp)
                PyModule: set_global_var(CURRENT_CELL_OBJ, A1)
                PyModule: update_with_result()
                libre_pythonista: CodeRules - get_matched_rule() found match rule: <CodeEmpty()>
            PySourceManager: _update_item() Leaving.
        PySourceManager: update_all() Leaving.
    CellMgr: reset_py_inst() Done
CellMgr: _on_calc_formulas_calculated() Done.
libre_pythonista: formulas_calc() Triggered CALC_FORMULAS_CALCULATED event.
CodeSheetModifyListener: Sheet Modified. Raising SHEET_MODIFIED event.
CellMgr: _on_sheet_modified() Entering.
CellMgr: _on_sheet_modified() Done.
CellMgr: _on_calc_pyc_formula_inserted() Entering.
    SheetMgr: Sheet calculate event already ensured
CellMgr: _on_calc_pyc_formula_inserted() Done.

```