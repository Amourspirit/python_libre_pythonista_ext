CS_PROTOCOL = "___lo_identifier___.ProtocolHandler.cs:"
MAIN_PROTOCOL = "___lo_identifier___.ProtocolHandler.ista:"
UNO_CS_CMD_START = f".uno:{CS_PROTOCOL}"

DISPATCH_PY_CODE_VALIDATE = f"{CS_PROTOCOL}libre_pythonista.calc.code.py.validate"
PATH_SEL_RNG = "libre_pythonista.calc.sel.rng"
DISPATCH_SEL_RNG = f"{CS_PROTOCOL}{PATH_SEL_RNG}"
DISPATCH_SEL_LP_FN = f"{CS_PROTOCOL}libre_pythonista.calc.sel.lp_fn"
PATH_CODE_DEL = "libre_pythonista.calc.code.del"
DISPATCH_CODE_DEL = f"{CS_PROTOCOL}{PATH_CODE_DEL}"

UNO_DISPATCH_CODE_EDIT = f"{CS_PROTOCOL}libre_pythonista.calc.code.edit"
UNO_DISPATCH_CODE_EDIT_MB = f"{CS_PROTOCOL}libre_pythonista.calc.code.edit.mb"
UNO_DISPATCH_DF_STATE = f"{CS_PROTOCOL}libre_pythonista.calc.code.df.state"
UNO_DISPATCH_DS_STATE = f"{CS_PROTOCOL}libre_pythonista.calc.code.ds.state"
UNO_DISPATCH_DATA_TBL_STATE = f"{CS_PROTOCOL}libre_pythonista.calc.code.data_tbl.state"
UNO_DISPATCH_PY_OBJ_STATE = f"{CS_PROTOCOL}libre_pythonista.calc.py_obj.state"

PATH_ABOUT = "libre_pythonista.ext.about"
PATH_CELL_CTl_UPDATE = "libre_pythonista.calc.cell.select_ctl_update"
PATH_CELL_SELECT = "libre_pythonista.calc.cell.select"
PATH_CELL_SELECT_RECALC = "libre_pythonista.calc.cell.select_recalc"
PATH_DATA_TBL_CARD = "libre_pythonista.calc.cell.data_tbl_card"
PATH_DF_CARD = "libre_pythonista.calc.cell.df_card"
PATH_LOG_WIN = "libre_pythonista.calc.log_window"
PATH_PIP_PKG_INSTALL = "libre_pythonista.ext.pip_pkg_install"
PATH_PIP_PKG_INSTALLED = "libre_pythonista.ext.pkg_pkg_installed"
PATH_PIP_PKG_LINK = "libre_pythonista.ext.pkg_pkg_link"
PATH_PIP_PKG_UNINSTALL = "libre_pythonista.ext.pip_pkg_uninstall"
PATH_PIP_PKG_UNLINK = "libre_pythonista.ext.pkg_pkg_unlink"
PATH_PYC_FORMULA = "libre_pythonista.insert_pyc_formula"
PATH_PYC_FORMULA_DEP = "libre_pythonista.insert_pyc_formula_dep"
DISPATCH_CELL_CTl_UPDATE = f"{CS_PROTOCOL}{PATH_CELL_CTl_UPDATE}"
DISPATCH_CELL_SELECT = f"{CS_PROTOCOL}{PATH_CELL_SELECT}"
DISPATCH_CELL_SELECT_RECALC = f"{CS_PROTOCOL}{PATH_CELL_SELECT_RECALC}"
DISPATCH_DATA_TBL_CARD = f"{CS_PROTOCOL}{PATH_DATA_TBL_CARD}"
DISPATCH_DF_CARD = f"{CS_PROTOCOL}{PATH_DF_CARD}"


def _get_formula_pyimpl() -> str:
    return f"___lo_identifier___.PyImpl".upper()


FORMULA_PYIMPL = _get_formula_pyimpl()
FORMULA_PYC = FORMULA_PYIMPL + ".PYC"
