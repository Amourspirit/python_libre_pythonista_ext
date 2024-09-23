UNO_DISPATCH_PY_CODE_VALIDATE = ".uno:libre_pythonista.calc.code.py.validate"
UNO_DISPATCH_SEL_RNG = ".uno:libre_pythonista.calc.sel.rng"
UNO_DISPATCH_SEL_LP_FN = ".uno:libre_pythonista.calc.sel.lp_fn"
UNO_DISPATCH_CODE_DEL = ".uno:libre_pythonista.calc.code.del"
UNO_DISPATCH_CODE_EDIT = ".uno:libre_pythonista.calc.code.edit"
UNO_DISPATCH_CODE_EDIT_MB = ".uno:libre_pythonista.calc.code.edit.mb"
UNO_DISPATCH_DF_STATE = ".uno:libre_pythonista.calc.code.df.state"
UNO_DISPATCH_DS_STATE = ".uno:libre_pythonista.calc.code.ds.state"
UNO_DISPATCH_DATA_TBL_STATE = ".uno:libre_pythonista.calc.code.data_tbl.state"
UNO_DISPATCH_PY_OBJ_STATE = ".uno:libre_pythonista.calc.py_obj.state"
UNO_DISPATCH_CELL_SELECT = ".uno:libre_pythonista.calc.cell.select"
UNO_DISPATCH_CELL_SELECT_RECALC = ".uno:libre_pythonista.calc.cell.select_recalc"
UNO_DISPATCH_CELL_CTl_UPDATE = ".uno:libre_pythonista.calc.cell.select_ctl_update"
UNO_DISPATCH_DF_CARD = ".uno:libre_pythonista.calc.cell.df_card"
UNO_DISPATCH_DATA_TBL_CARD = ".uno:libre_pythonista.calc.cell.data_tbl_card"
UNO_DISPATCH_ABOUT = ".uno:libre_pythonista.ext.about"
UNO_DISPATCH_LOG_WIN = ".uno:libre_pythonista.calc.log_window"
UNO_DISPATCH_INSTALL_PIP_PKG = ".uno:libre_pythonista.ext.install_pip_pkg"


def _get_formula_pyimpl():
    return f"___lo_identifier___.PyImpl".upper()


FORMULA_PYIMPL = _get_formula_pyimpl()
FORMULA_PYC = FORMULA_PYIMPL + ".PYC"
