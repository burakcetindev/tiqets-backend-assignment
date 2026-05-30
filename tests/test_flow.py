import logging
import sys

from main import VoucherPipeline


def build_test_logger() -> logging.Logger:
    """Create a logger for flow tests."""
    logger = logging.getLogger("flow-test")
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def test_flow_runs_end_to_end(tmp_path: object) -> None:
    """Run the full pipeline through the CLI orchestration class."""
    pipeline = VoucherPipeline(build_test_logger())
    output_path = tmp_path / "flow.csv"

    pipeline.run(
        "tests/fixtures/orders_valid.csv",
        "tests/fixtures/barcodes_valid.csv",
        str(output_path),
    )

    assert output_path.exists()
