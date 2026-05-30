from src.models.barcode import Barcode
from src.models.order import Order
from src.processors.processor import Processor


def test_processor_builds_output() -> None:
    """Ensure the processor groups barcodes per order."""
    orders = [Order(order_id="1", customer_id="10"), Order(order_id="2", customer_id="11")]
    barcodes = [
        Barcode(barcode="111", order_id="1"),
        Barcode(barcode="112", order_id="1"),
        Barcode(barcode="113", order_id="2"),
        Barcode(barcode="999", order_id=None),
    ]

    processor = Processor()
    records = processor.process(orders, barcodes)

    assert records[0]["barcodes"] == ["111", "112"]
    assert records[1]["barcodes"] == ["113"]


def test_processor_summaries() -> None:
    """Ensure the processor reports top customers and unused counts."""
    orders = [Order(order_id="1", customer_id="10"), Order(order_id="2", customer_id="10")]
    barcodes = [Barcode(barcode="111", order_id="1"), Barcode(barcode="112", order_id=None)]

    processor = Processor()
    records = processor.process(orders, barcodes)

    assert processor.get_top_customers(records, n=1) == [("10", 1)]
    assert processor.get_unused_barcode_count(barcodes) == 1
