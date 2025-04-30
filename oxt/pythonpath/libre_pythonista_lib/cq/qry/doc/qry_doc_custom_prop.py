from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_office_doc_t import QryOfficeDocT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.doc.qry_office_doc_t import QryOfficeDocT

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_version.py


class QryDocCustomProp(QryBase, QryOfficeDocT[Any]):
    def __init__(self, doc: OfficeDocumentT, name: str, default: Any = NULL_OBJ) -> None:  # noqa: ANN401
        QryBase.__init__(self)
        self._doc = doc
        self._name = name
        self._default = default

    def execute(self) -> Any:  # noqa: ANN401
        """
        Executes the query to get the document custom property value.

        Returns:
            Any: The custom property value if successful, otherwise Default or ``NULL_OBJ``.
                If no default is provided, ``NULL_OBJ`` is returned when the query fails.

        Note:
            ``NULL_OBJ`` can be imported from ``ooodev.utils.gen_util``.
        """
        return self._doc.get_custom_property(self._name, default=self._default)  # type: ignore
