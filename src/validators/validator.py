"""Validation logic to enforce assignment rules on orders and barcodes.

This module provides `Validator` which filters malformed rows, rejects
barcodes referencing unknown orders, removes duplicate barcodes, and drops
orders without associated barcodes.
"""

import logging
from collections import Counter

from src.models.barcode import Barcode
from src.models.order import Order


class Validator:
    """Validates orders and barcodes against assignment rules."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the validator.

        Args:
            logger (logging.Logger): Logger for validation warnings.

        Returns:
            None
        """
        self._logger = logger

    def validate(self, orders: list[Order], barcodes: list[Barcode]) -> tuple[list[Order], list[Barcode]]:
        """Validate orders and barcodes.

        Args:
            orders (list[Order]): Parsed orders.
            barcodes (list[Barcode]): Parsed barcodes.

        Returns:
            tuple[list[Order], list[Barcode]]: Clean orders and barcodes.
        """
        clean_orders = self._filter_invalid_orders(orders)
        clean_barcodes = self._filter_invalid_barcodes(barcodes, {o.order_id for o in clean_orders})
        clean_barcodes = self._remove_duplicate_barcodes(clean_barcodes)
        clean_orders = self._remove_orders_without_barcodes(clean_orders, clean_barcodes)
        return clean_orders, clean_barcodes

    def _filter_invalid_orders(self, orders: list[Order]) -> list[Order]:
        """Drop orders missing required values.

        Args:
            orders (list[Order]): Parsed orders.

        Returns:
            list[Order]: Valid orders.
        """
        cleaned: list[Order] = []
        for order in orders:
            if not order.order_id or not order.customer_id:
                self._logger.warning("Invalid order ignored: %s", order)
                continue
            cleaned.append(order)
        return cleaned

    def _filter_invalid_barcodes(self, barcodes: list[Barcode], order_ids: set[str]) -> list[Barcode]:
        """Drop barcodes missing values or referencing unknown orders.

        Args:
            barcodes (list[Barcode]): Parsed barcodes.
            order_ids (set[str]): Known order ids.

        Returns:
            list[Barcode]: Valid barcodes.
        """
        cleaned: list[Barcode] = []
        for barcode in barcodes:
            if not barcode.barcode:
                self._logger.warning("Missing barcode ignored: %s", barcode)
                continue
            if barcode.order_id and barcode.order_id not in order_ids:
                self._logger.warning("Unknown order_id for barcode %s: %s", barcode.barcode, barcode.order_id)
                continue
            cleaned.append(barcode)
        return cleaned

    def _remove_duplicate_barcodes(self, barcodes: list[Barcode]) -> list[Barcode]:
        """Remove duplicate barcodes and log all occurrences.

        Args:
            barcodes (list[Barcode]): Validated barcodes.

        Returns:
            list[Barcode]: Barcodes without duplicates.
        """
        counts = Counter(barcode.barcode for barcode in barcodes)
        duplicates = {value for value, count in counts.items() if count > 1}
        if not duplicates:
            return barcodes
        for barcode in barcodes:
            if barcode.barcode in duplicates:
                self._logger.warning(
                    "Duplicate barcode ignored: %s (order_id=%s)",
                    barcode.barcode,
                    barcode.order_id,
                )
        return [barcode for barcode in barcodes if barcode.barcode not in duplicates]

    def _remove_orders_without_barcodes(self, orders: list[Order], barcodes: list[Barcode]) -> list[Order]:
        """Remove orders that have no associated barcodes.

        Args:
            orders (list[Order]): Validated orders.
            barcodes (list[Barcode]): Validated barcodes.

        Returns:
            list[Order]: Orders with barcodes.
        """
        order_ids_with_barcodes = {barcode.order_id for barcode in barcodes if barcode.order_id}
        cleaned: list[Order] = []
        for order in orders:
            if order.order_id not in order_ids_with_barcodes:
                self._logger.warning("Order has no barcodes and was ignored: %s", order.order_id)
                continue
            cleaned.append(order)
        return cleaned
