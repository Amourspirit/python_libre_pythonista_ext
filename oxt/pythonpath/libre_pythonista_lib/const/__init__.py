UNO_CS_PROTOCOL = ".___lo_identifier___.ProtocolHandler.cs:"
UNO_MAIN_PROTOCOL = "___lo_identifier___.ProtocolHandler.ista:"
UNO_CS_CMD_START = f".uno:{UNO_CS_PROTOCOL}"
UNO_DISPATCH_PY_CODE_VALIDATE = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.code.py.validate"
UNO_DISPATCH_SEL_RNG = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.sel.rng"
UNO_DISPATCH_SEL_LP_FN = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.sel.lp_fn"
UNO_DISPATCH_CODE_DEL = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.code.del"
UNO_DISPATCH_CODE_EDIT = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.code.edit"
UNO_DISPATCH_CODE_EDIT_MB = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.code.edit.mb"
UNO_DISPATCH_DF_STATE = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.code.df.state"
UNO_DISPATCH_DS_STATE = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.code.ds.state"
UNO_DISPATCH_DATA_TBL_STATE = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.code.data_tbl.state"
UNO_DISPATCH_PY_OBJ_STATE = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.py_obj.state"

UNO_DISPATCH_CELL_SELECT = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.cell.select"
UNO_DISPATCH_CELL_SELECT_RECALC = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.cell.select_recalc"
UNO_DISPATCH_CELL_CTl_UPDATE = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.cell.select_ctl_update"
UNO_DISPATCH_DF_CARD = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.cell.df_card"
UNO_DISPATCH_DATA_TBL_CARD = f"{UNO_CS_PROTOCOL}libre_pythonista.calc.cell.data_tbl_card"
UNO_DISPATCH_ABOUT = "libre_pythonista.ext.about"
UNO_DISPATCH_LOG_WIN = "libre_pythonista.calc.log_window"
UNO_DISPATCH_PIP_PKG_INSTALL = "libre_pythonista.ext.pip_pkg_install"
UNO_DISPATCH_PIP_PKG_UNINSTALL = "libre_pythonista.ext.pip_pkg_uninstall"
UNO_DISPATCH_PIP_PKG_INSTALLED = "libre_pythonista.ext.pkg_pkg_installed"
UNO_DISPATCH_PIP_PKG_LINK = "libre_pythonista.ext.pkg_pkg_link"
UNO_DISPATCH_PIP_PKG_UNLINK = "libre_pythonista.ext.pkg_pkg_unlink"
UNO_DISPATCH_PYC_FORMULA = "libre_pythonista.insert_pyc_formula"
UNO_DISPATCH_PYC_FORMULA_DEP = "libre_pythonista.insert_pyc_formula_dep"


def _get_formula_pyimpl() -> str:
    return f"___lo_identifier___.PyImpl".upper()


FORMULA_PYIMPL = _get_formula_pyimpl()
FORMULA_PYC = FORMULA_PYIMPL + ".PYC"
