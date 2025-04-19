CB_DOC_FOCUS_GAINED = "cb_doc_focus_gain"
CB_DOC_FOCUS_LOST = "cb_doc_focus_lost"
DOCUMENT_FOCUS_GAINED = "document_focus_gain"
DOCUMENT_FOCUS_LOST = "document_focus_lost"
DOCUMENT_SAVING = "document_saving"
OXT_INIT = "oxt_init"
GBL_DOC_CLOSING = "librepythonista_doc_closing"
LOG_OPTIONS_CHANGED = "log_options_changed"
LOG_PY_LOGGER_RESET = "py_logger_reset"
SHEET_MODIFIED = "calc_sheet_modified"
SHEET_ACTIVATION = "calc_sheet_activation"
SHEET_CELL_MOVED = "calc_sheet_cell_moved"
CALC_FORMULAS_CALCULATED = "calc_formulas_calculated"
"""
CALC_FORMULAS_CALCULATED event is triggered when the formulas are calculated.
This only occurs when the share_event.formulas_calc() macro is triggered.
"""
PYC_FORMULA_INSERTING = "lp_pyc_formula_inserting"
PYC_FORMULA_INSERTED = "lp_pyc_formula_inserted"
PYC_FORMULA_ENTER = "lp_pyc_formula_enter"
PYC_RULE_MATCH_DONE = "pyc_rule_match_done"
DOCUMENT_EVENT = "calc_document_event"
LP_DISPATCHING_CMD = "lp_dispatching_cmd"
LP_DISPATCHED_CMD = "lp_dispatched_cmd"
LP_DOC_EVENTS_ENSURED = "lp_doc_events_ensured"
"""
LP_DOC_EVENTS_ENSURED event is triggered when the document events are ensured.
This takes place in the CalcDocMgr._ensure_events() method.
"""

# region cell.ctl shared events
CONTROL_ADDED = "control_added"
CONTROL_ADDING = "control_adding"
CONTROL_REMOVED = "control_removed"
CONTROL_REMOVING = "control_removing"
CONTROL_UPDATING = "control_updating"
CONTROL_UPDATED = "control_updated"
CONTROL_INSERTING_CELL_IMG_LINKED = "control_insert_cell_img_linked"
CONTROL_INSERTED_CELL_IMG_LINKED = "control_inserted_cell_img_linked"
# endregion cell.ctl shared events

DOC_GBL_DEL_INSTANCE = "doc_gbl_del_instance"

GLB_MODULE_SET_GBL_VAR = "glb_module_set_gbl_var"
