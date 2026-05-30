import pytest

from src.models.barcode import Barcode
from src.models.order import Order
from src.readers.barcode_reader import BarcodeReader
from src.readers.order_reader import OrderReader


def test_order_reader_reads_rows() -> None:
    """Ensure the order reader returns parsed models."""
    reader = OrderReader()
    rows = reader.read("tests/fixtures/orders_valid.csv")
    assert rows[0] == Order(order_id="1", customer_id="100")


def test_barcode_reader_reads_rows() -> None:
    """Ensure the barcode reader parses optional order ids."""
    reader = BarcodeReader()
    rows = reader.read("tests/fixtures/barcodes_valid.csv")
    assert rows[0] == Barcode(barcode="11111111111", order_id="1")
    assert rows[-1] == Barcode(barcode="11111111115", order_id=None)


def test_reader_missing_file_raises() -> None:
    """Ensure missing files raise a clear error."""
    reader = OrderReader()
    with pytest.raises(FileNotFoundError):
        reader.read("tests/fixtures/missing.csv")


def test_empty_files_return_no_rows() -> None:
    """Ensure empty fixture files return no rows."""
    order_reader = OrderReader()
    barcode_reader = BarcodeReader()

    assert order_reader.read("tests/fixtures/orders_empty.csv") == []
    assert barcode_reader.read("tests/fixtures/barcodes_empty.csv") == []
