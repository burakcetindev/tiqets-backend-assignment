import argparse
import logging
import sys

from src.processors.processor import Processor
from src.readers.barcode_reader import BarcodeReader
from src.readers.order_reader import OrderReader
from src.reporter.reporter import Reporter
from src.validators.validator import Validator
from src.writers.output_writer import OutputWriter

# Sample data in assignment/ is read-only. Working data lives in data/


class VoucherPipeline:
    """Orchestrates the voucher pipeline from input to output."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the pipeline.

        Args:
            logger (logging.Logger): Logger for validation output.

        Returns:
            None
        """
        self._logger = logger
        self._validator = Validator(logger)
        self._processor = Processor()
        self._reporter = Reporter()

    def run(self, orders_path: str, barcodes_path: str, output_path: str) -> None:
        """Run the pipeline end-to-end.

        Args:
            orders_path (str): Path to orders CSV.
            barcodes_path (str): Path to barcodes CSV.
            output_path (str): Path to output CSV.

        Returns:
            None

        Raises:
            FileNotFoundError: When input files are missing.
            ValueError: When input files are malformed.
            OSError: When output cannot be written.
        """
        orders = OrderReader().read(orders_path)
        barcodes = BarcodeReader().read(barcodes_path)
        orders, barcodes = self._validator.validate(orders, barcodes)
        records = self._processor.process(orders, barcodes)
        OutputWriter().write(records, output_path)
        top_customers = self._processor.get_top_customers(records, n=5)
        unused_count = self._processor.get_unused_barcode_count(barcodes)
        self._reporter.print_top_customers(top_customers)
        self._reporter.print_unused_barcodes(unused_count)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Args:
        None

    Returns:
        argparse.ArgumentParser: Configured argument parser.

    Raises:
        None
    """
    parser = argparse.ArgumentParser(description="Tiqets voucher pipeline")
    parser.add_argument(
        "--orders",
        default="data/orders.csv",
        help="Path to orders CSV (default: data/orders.csv)",
    )
    parser.add_argument(
        "--barcodes",
        default="data/barcodes.csv",
        help="Path to barcodes CSV (default: data/barcodes.csv)",
    )
    parser.add_argument(
        "--output",
        default="output/result.csv",
        help="Path to output CSV (default: output/result.csv)",
    )
    return parser


def configure_logging() -> logging.Logger:
    """Configure and return the application logger.

    Args:
        None

    Returns:
        logging.Logger: Configured logger.

    Raises:
        None
    """
    logger = logging.getLogger("tiqets")
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def main() -> None:
    """Entry point for the CLI.

    Args:
        None

    Returns:
        None

    Raises:
        SystemExit: When argparse exits.
    """
    args = build_parser().parse_args()
    logger = configure_logging()
    pipeline = VoucherPipeline(logger)
    try:
        pipeline.run(args.orders, args.barcodes, args.output)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
