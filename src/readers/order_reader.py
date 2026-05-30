from src.models.order import Order

from .base_reader import BaseReader


class OrderReader(BaseReader):
    """Reads orders from CSV."""

    def read(self, filepath: str) -> list[Order]:
        """Read and parse order rows.

        Args:
            filepath (str): Path to orders CSV.

        Returns:
            list[Order]: Parsed orders.

        Raises:
            FileNotFoundError: When the file does not exist.
            ValueError: When required headers are missing.
        """
        rows = self._read_rows(filepath, ["order_id", "customer_id"])
        return [Order(order_id=row["order_id"], customer_id=row["customer_id"]) for row in rows]
