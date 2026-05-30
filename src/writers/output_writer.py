import csv
from pathlib import Path


class OutputWriter:
    """Writes output rows to a CSV file."""

    def write(self, records: list[dict[str, object]], filepath: str) -> None:
        """Write output rows to disk.

        Args:
            records (list[dict[str, object]]): Output records to write.
            filepath (str): Path to the output CSV file.

        Returns:
            None

        Raises:
            OSError: When the output file cannot be written.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["customer_id", "order_id", "barcodes"])
            for record in records:
                writer.writerow(
                    [
                        record["customer_id"],
                        record["order_id"],
                        self._format_barcodes(record["barcodes"]),
                    ]
                )

    def _format_barcodes(self, barcodes: object) -> str:
        """Format barcodes for CSV output.

        Args:
            barcodes (object): List of barcodes.

        Returns:
            str: Formatted barcode list string.

        Raises:
            ValueError: When barcodes are not a list of strings.
        """
        if not isinstance(barcodes, list):
            raise ValueError("Barcodes must be a list of strings.")
        formatted = ", ".join(f"'{barcode}'" for barcode in barcodes)
        return f"[{formatted}]"
