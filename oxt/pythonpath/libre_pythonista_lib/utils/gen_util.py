from __future__ import annotations


class GenUtil:
    @staticmethod
    def create_cell_addr_query_str(sheet_idx: int, cell_addr: str) -> str:
        """
        Creates a property cell address.

        Args:
            sheet_idx (int): The index of the sheet.
            cell_addr (str): The cell address such as ``A1``.

        Returns:
            str: The property cell address in the format of ``sheet_index=0&cell_addr=A1``
        """
        return f"sheet_index={sheet_idx}&cell_addr={cell_addr}"
