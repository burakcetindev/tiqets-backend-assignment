import logging
import sys

from src.processors.processor import Processor
from src.readers.barcode_reader import BarcodeReader
from src.readers.order_reader import OrderReader
from src.reporter.reporter import Reporter
from src.validators.validator import Validator
from src.writers.output_writer import OutputWriter


def build_test_logger() -> logging.Logger:
    """Create a logger for integration tests."""
    logger = logging.getLogger("integration-test")
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def test_pipeline_end_to_end(tmp_path: object) -> None:
    """Run the pipeline using fixture data and validate outputs."""
    logger = build_test_logger()
    validator = Validator(logger)

    orders = OrderReader().read("tests/fixtures/orders_valid.csv")
    barcodes = BarcodeReader().read("tests/fixtures/barcodes_valid.csv")

    orders, barcodes = validator.validate(orders, barcodes)

    processor = Processor()
    records = processor.process(orders, barcodes)

    output_path = tmp_path / "result.csv"
    OutputWriter().write(records, str(output_path))

    reporter = Reporter()
    top_customers = processor.get_top_customers(records, n=2)

    assert output_path.exists()
    assert processor.get_unused_barcode_count(barcodes) == 1
    reporter.print_top_customers(top_customers)
