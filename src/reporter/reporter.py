"""Reporting helpers for pipeline summaries printed to stdout."""

class Reporter:
    """Prints pipeline summaries to stdout."""

    def print_top_customers(self, top_customers: list[tuple[str, int]]) -> None:
        """Print top customers with ticket counts.

        Args:
            top_customers (list[tuple[str, int]]): Customer counts.

        Returns:
            None
        """
        for customer_id, ticket_count in top_customers:
            print(f"{customer_id}, {ticket_count}")

    def print_unused_barcodes(self, count: int) -> None:
        """Print the unused barcode count.

        Args:
            count (int): Unused barcode count.

        Returns:
            None
        """
        print(f"Unused barcodes: {count}")
