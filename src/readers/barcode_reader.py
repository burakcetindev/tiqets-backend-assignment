from typing import Optional

from src.models.barcode import Barcode

from .base_reader import BaseReader


class BarcodeReader(BaseReader):
    """Reads barcodes from CSV."""

    def read(self, filepath: str) -> list[Barcode]:
        """Read and parse barcode rows.

        Args:
            filepath (str): Path to barcodes CSV.

        Returns:
            list[Barcode]: Parsed barcodes.

        Raises:
            FileNotFoundError: When the file does not exist.
            ValueError: When required headers are missing.
        """
        rows = self._read_rows(filepath, ["barcode", "order_id"])
        return [Barcode(barcode=row["barcode"], order_id=self._to_optional(row["order_id"])) for row in rows]

    def _to_optional(self, raw_value: str) -> Optional[str]:
        """Normalize optional order ids.

        Args:
            raw_value (str): Raw order id value.

        Returns:
            Optional[str]: Normalized order id or None.

        Raises:
            None
        """
        value = raw_value.strip()
        return value if value else None
