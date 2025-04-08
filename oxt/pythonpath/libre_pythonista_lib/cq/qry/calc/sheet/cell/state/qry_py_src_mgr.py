from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcDoc

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
else:
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager


# tested in: tests/test_cmd/test_cmd_append_code.py

# TODO: Move this class to cq/qry/calc/doc/


class QryPySrcMgrCode(QryBase, QryT[PySourceManager]):
    """
    Query class that retrieves a PySourceManager instance for a given cell.

    This class manages the retrieval of Python source code associated with a specific cell
    in a LibreOffice Calc document.
    """

    def __init__(self, doc: CalcDoc, mod: PyModuleT | None = None) -> None:
        """
        Initialize the query with a cell and optional Python module.

        Args:
            doc: (CalcDoc) The CalcDoc instance to query
            mod: (PyModuleT, optional) Optional Python module. If not provided, will be queried when needed
        """
        QryBase.__init__(self)
        self._doc = doc
        self._mod = mod

    def _qry_mod(self) -> PyModuleT:
        """
        Gets the Python module via query.

        Returns:
            PyModuleT: The default Python module for the document
        """
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def execute(self) -> PySourceManager:
        """
        Executes the query to create a new PySourceManager instance.

        Returns:
            PySourceManager: A new source manager instance for the cell's document
        """
        return PySourceManager(doc=self._doc, mod=self.mod)

    @property
    def mod(self) -> PyModuleT:
        """
        Get the Python module associated with this query.

        Returns:
            PyModuleT: The Python module instance, querying it if not already set
        """
        if self._mod is None:
            self._mod = self._qry_mod()
        return self._mod
