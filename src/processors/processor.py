from collections import Counter

from src.models.barcode import Barcode
from src.models.order import Order


class Processor:
    """Core join and aggregation logic."""

    def process(self, orders: list[Order], barcodes: list[Barcode]) -> list[dict[str, object]]:
        """Join orders with barcodes into output records.

        Args:
            orders (list[Order]): Validated orders.
            barcodes (list[Barcode]): Validated barcodes.

        Returns:
            list[dict[str, object]]: Output records.

        Raises:
            None
        """
        barcode_map = self._group_barcodes(barcodes)
        records: list[dict[str, object]] = []
        for order in orders:
            records.append(
                {
                    "customer_id": order.customer_id,
                    "order_id": order.order_id,
                    "barcodes": barcode_map.get(order.order_id, []),
                }
            )
        return records

    def get_top_customers(self, records: list[dict[str, object]], n: int = 5) -> list[tuple[str, int]]:
        """Calculate top customers by ticket count.

        Args:
            records (list[dict[str, object]]): Output records.
            n (int): Number of customers to return.

        Returns:
            list[tuple[str, int]]: Sorted (customer_id, count).

        Raises:
            None
        """
        counts: Counter[str] = Counter()
        for record in records:
            customer_id = str(record["customer_id"])
            barcodes = record["barcodes"]
            counts[customer_id] += len(barcodes)
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return ordered[:n]

    def get_unused_barcode_count(self, barcodes: list[Barcode]) -> int:
        """Count barcodes without an order assignment.

        Args:
            barcodes (list[Barcode]): Validated barcodes.

        Returns:
            int: Count of unused barcodes.

        Raises:
            None
        """
        return sum(1 for barcode in barcodes if barcode.order_id is None)

    def _group_barcodes(self, barcodes: list[Barcode]) -> dict[str, list[str]]:
        """Group sold barcodes by order id.

        Args:
            barcodes (list[Barcode]): Validated barcodes.

        Returns:
            dict[str, list[str]]: Barcodes grouped per order.

        Raises:
            None
        """
        grouped: dict[str, list[str]] = {}
        for barcode in barcodes:
            if barcode.order_id is None:
                continue
            grouped.setdefault(barcode.order_id, []).append(barcode.barcode)
        return grouped
