import logging
import sys

from src.readers.barcode_reader import BarcodeReader
from src.readers.order_reader import OrderReader
from src.validators.validator import Validator


def build_test_logger() -> logging.Logger:
    """Create a logger that emits warnings to stderr."""
    logger = logging.getLogger("validator-test")
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def test_validator_filters_invalid_rows(capsys: object) -> None:
    """Validate that duplicates and missing values are ignored."""
    logger = build_test_logger()
    validator = Validator(logger)
    orders = OrderReader().read("tests/fixtures/orders_edge.csv")
    barcodes = BarcodeReader().read("tests/fixtures/barcodes_edge.csv")

    clean_orders, clean_barcodes = validator.validate(orders, barcodes)

    assert {order.order_id for order in clean_orders} == {"1", "2"}
    assert all(barcode.barcode != "20000000000" for barcode in clean_barcodes)

    captured = capsys.readouterr()
    assert "Duplicate barcode" in captured.err
    assert "Order has no barcodes" in captured.err


def test_validator_handles_empty_inputs() -> None:
    """Ensure empty datasets validate cleanly."""
    logger = build_test_logger()
    validator = Validator(logger)
    orders = OrderReader().read("tests/fixtures/orders_empty.csv")
    barcodes = BarcodeReader().read("tests/fixtures/barcodes_empty.csv")

    clean_orders, clean_barcodes = validator.validate(orders, barcodes)

    assert clean_orders == []
    assert clean_barcodes == []
